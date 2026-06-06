"""RAGAS evaluator clients backed by local Ollama models.

RAGAS 0.4.x talks to any OpenAI-compatible endpoint through its own
``llm_factory`` / ``embedding_factory``. Ollama exposes exactly such an
endpoint, so no provider-specific RAGAS adapter (and no langchain-ollama) is
needed — the stock ``openai`` client, already a RAGAS dependency, is enough.

Verified against RAGAS 0.4 docs:
- getstarted/evals.md, howtos/llm-adapters.md  (LLM via llm_factory + OpenAI client)
- migrations/migrate_from_v03_to_v04.md        (embedding_factory v0.4 signature)
"""

from openai import AsyncOpenAI, OpenAI
from ragas.embeddings import embedding_factory
from ragas.llms import llm_factory

from ragas_lab.config import settings


def build_judge_llm():
    """The evaluator LLM (the "judge"). Used by metrics such as Faithfulness."""
    client = OpenAI(api_key="ollama", base_url=settings.ollama_openai_base_url)
    return llm_factory(settings.ollama_judge_model, provider="openai", client=client)


def build_judge_embeddings():
    """The evaluator embeddings. Used by metrics such as AnswerRelevancy."""
    client = AsyncOpenAI(api_key="ollama", base_url=settings.ollama_openai_base_url)
    return embedding_factory(
        provider="openai", model=settings.ollama_embed_model, client=client
    )
