"""Lesson 05 — a minimal, runnable, naive RAG pipeline.

This is the baseline the rest of the handbook measures and improves. It wires the
four stages of Lesson 03 end to end with the LangChain orchestration framework:

    load  ->  chunk  ->  embed (index)  ->  retrieve  ->  augment + generate

Everything is deliberately the simplest thing that works: a tiny on-disk corpus,
a fixed-size character splitter, an in-memory vector store, top-k similarity
search, and a single grounded prompt. No reranking, no query rewriting, no
evaluation — those come later. Run it with real output:

    uv run python -m lessons.05-minimal-end-to-end-rag.demo

The Ollama endpoint and the model names are read from .env via
ragas_lab.config.settings (one place to pin them). The run shown in the lesson used:
  - generation model : qwen3:14b           (served by Ollama)
  - embedding model  : qwen3-embedding:4b  (served by Ollama, 2560-dim vectors)
  - LangChain        : 0.3.x line (see pyproject.toml); langchain-ollama 0.3.x
Results still vary slightly run to run — LLM generation is not bit-for-bit
deterministic even at temperature 0.
"""

from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ragas_lab.config import settings

# --- Configuration ------------------------------------------------------------
# The endpoint and the model names all come from ragas_lab.config.settings, which
# reads them from .env (the run below used qwen3:14b / qwen3-embedding:4b). Pinning
# lives in one place — change .env, not this file — so the pipeline and any later
# evaluation agree on which models produced a result.
CHAT_MODEL = settings.ollama_chat_model
EMBED_MODEL = settings.ollama_embed_model
DATA_DIR = Path(__file__).parent / "data"
TOP_K = 3
QUESTION = "How do I cancel my subscription, and will I get a refund?"


def banner(text: str) -> None:
    print(f"\n{'=' * 70}\n{text}\n{'=' * 70}")


def main() -> None:
    print(f"Ollama endpoint: {settings.ollama_base_url}")

    # --- 1. LOAD -------------------------------------------------------------
    # Read each .txt help-desk article into a LangChain Document. "Loading" is
    # the framework's job of turning raw files into a uniform Document object
    # (page_content + metadata) the rest of the pipeline can consume.
    banner("1. LOAD")
    docs = []
    for path in sorted(DATA_DIR.glob("*.txt")):
        docs.extend(TextLoader(str(path)).load())
    print(f"Loaded {len(docs)} documents from {DATA_DIR.name}/:")
    for d in docs:
        print(f"  - {Path(d.metadata['source']).name}  ({len(d.page_content)} chars)")

    # --- 2. CHUNK ------------------------------------------------------------
    # Split each document into smaller, overlapping pieces. Retrieval works on
    # chunks, not whole files, so a query matches a focused passage instead of a
    # whole article. Why these sizes and how to choose them is the ingestion
    # lessons' job; here we just take a small, sane default.
    banner("2. CHUNK")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(
        f"Split {len(docs)} documents into {len(chunks)} chunks (chunk_size=500, chunk_overlap=50)."
    )

    # --- 3. EMBED + INDEX ----------------------------------------------------
    # Turn each chunk into a vector (Lesson 02) with the embedding model, and put
    # the vectors in a store we can search. InMemoryVectorStore keeps them in a
    # plain Python dict — no database — which is all a baseline needs.
    banner("3. EMBED + INDEX")
    embeddings = OllamaEmbeddings(model=EMBED_MODEL, base_url=settings.ollama_base_url)
    store = InMemoryVectorStore(embeddings)
    store.add_documents(chunks)
    dim = len(embeddings.embed_query("probe"))
    print(
        f"Embedded {len(chunks)} chunks with '{EMBED_MODEL}' "
        f"({dim}-dim vectors) and indexed them in memory."
    )

    # --- 4. RETRIEVE ---------------------------------------------------------
    # Embed the question with the SAME model and return the TOP_K nearest chunks
    # by vector similarity. These are the only pieces of the corpus the LLM will
    # see — retrieval quality caps answer quality.
    banner("4. RETRIEVE")
    print(f"Question: {QUESTION}\n")
    retriever = store.as_retriever(search_kwargs={"k": TOP_K})
    retrieved = retriever.invoke(QUESTION)
    print(f"Top {TOP_K} retrieved chunks:")
    for i, d in enumerate(retrieved, 1):
        snippet = " ".join(d.page_content.split())[:90]
        print(f"  [{i}] {Path(d.metadata['source']).name}: {snippet}...")

    # --- 5. AUGMENT + GENERATE ----------------------------------------------
    # Build the prompt by inserting the retrieved chunks as context, then ask the
    # LLM to answer ONLY from that context and to abstain otherwise (the grounding
    # + abstention craft introduced in Lesson 04). This is what makes the answer
    # traceable to the corpus instead of to the model's frozen weights.
    banner("5. AUGMENT + GENERATE")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a help-desk assistant for Acme Cloud. Answer the question using "
                "ONLY the context below. If the answer is not in the context, say you "
                "don't know rather than guessing. Be concise.\n\nContext:\n{context}",
            ),
            ("human", "{question}"),
        ]
    )
    llm = ChatOllama(model=CHAT_MODEL, base_url=settings.ollama_base_url, temperature=0)

    def format_docs(docs_):
        return "\n\n".join(d.page_content for d in docs_)

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": format_docs(retrieved), "question": QUESTION})
    print(f"Answer:\n{answer.strip()}")


if __name__ == "__main__":
    main()
