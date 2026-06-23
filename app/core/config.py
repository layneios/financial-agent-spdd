from typing import Literal
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    pg_dsn: str
    llm_provider: Literal["ollama", "openrouter"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "gemma3:27b"
    ollama_ops_model: str = "qwen3.5:4b"
    embedding_model: str = "nomic-embed-text"
    embedding_dim: int = 768
    openrouter_api_key: str | None = None
    openrouter_model: str = "gpt-4.1-mini"
    log_format: Literal["json", "text"] = "text"

    @model_validator(mode="after")
    def _require_openrouter_key(self) -> "Settings":
        if self.llm_provider == "openrouter" and not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY required when LLM_PROVIDER=openrouter")
        return self

def get_settings() -> Settings:
    return Settings()  # Task 1 will replace with @lru_cache