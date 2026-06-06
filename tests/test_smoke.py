"""Smoke tests for the scaffolding itself.

No network and no Ollama required — these only guard that config loads and
imports resolve, so a broken setup fails fast and cheaply.
"""

from ragas_lab.config import Settings, settings


def test_settings_have_sane_defaults():
    assert settings.ollama_base_url.startswith("http")
    assert settings.ollama_judge_model
    assert settings.ollama_embed_model


def test_openai_base_url_appends_v1_and_strips_trailing_slash():
    s = Settings(ollama_base_url="http://localhost:11434/")
    assert s.ollama_openai_base_url == "http://localhost:11434/v1"
