from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    anthropic_api_key: str = ""

    embedding_model: str = "text-embedding-3-small"
    generation_model: str = "claude-sonnet-4-6"

    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 4

    chroma_persist_dir: str = "./chroma_data"
    chroma_collection: str = "documents"


settings = Settings()