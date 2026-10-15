from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "project-assistant"
    DATABASE_URL: str = "postgresql+psycopg://assistant:assistantpass@db:5432/assistant"

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str | None = None
    OLLAMA_BASE_URL: str = "http://ollama:11434/v1"

    DEFAULT_LLM_PROVIDER: str = "openai"
    DEFAULT_LLM_MODEL: str = "gpt-4.1-mini"
    DEFAULT_LLM_TEMPERATURE: float = 0.2

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()