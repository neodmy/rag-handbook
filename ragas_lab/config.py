"""Project configuration.

Loads settings from environment variables (and a local ``.env``) via
pydantic-settings. Every knob that affects an evaluation lives here on purpose:
the judge model and its endpoint are part of the *result*, not an
implementation detail. Pin them, and your scores are reproducible.
"""

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Ollama exposes an OpenAI-compatible API at ``${ollama_base_url}/v1``.
    ollama_base_url: str = "http://localhost:11434"
    # The generation (chat) model used by application code, e.g. a RAG pipeline's
    # generator. Reads OLLAMA_CHAT_MODEL, or the legacy OLLAMA_MODEL as a fallback.
    ollama_chat_model: str = Field(
        default="qwen3:14b",
        validation_alias=AliasChoices("ollama_chat_model", "ollama_model"),
    )
    # The evaluator ("judge") model used by RAGAS metrics — separate on purpose:
    # the system under test and the system that grades it should be pinned apart.
    ollama_judge_model: str = "mistral"
    ollama_embed_model: str = "nomic-embed-text"

    @property
    def ollama_openai_base_url(self) -> str:
        """The OpenAI-compatible endpoint the OpenAI client / RAGAS expects."""
        return f"{self.ollama_base_url.rstrip('/')}/v1"


settings = Settings()
