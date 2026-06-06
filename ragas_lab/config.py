"""Project configuration.

Loads settings from environment variables (and a local ``.env``) via
pydantic-settings. Every knob that affects an evaluation lives here on purpose:
the judge model and its endpoint are part of the *result*, not an
implementation detail. Pin them, and your scores are reproducible.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Ollama exposes an OpenAI-compatible API at ``${ollama_base_url}/v1``.
    ollama_base_url: str = "http://localhost:11434"
    ollama_judge_model: str = "mistral"
    ollama_embed_model: str = "nomic-embed-text"

    @property
    def ollama_openai_base_url(self) -> str:
        """The OpenAI-compatible endpoint the OpenAI client / RAGAS expects."""
        return f"{self.ollama_base_url.rstrip('/')}/v1"


settings = Settings()
