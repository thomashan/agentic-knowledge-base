from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Manages all runtime configuration for the application, loaded from environment variables.
    """

    # LLM Config
    llm_model: str
    llm_provider: str
    llm_base_url: str

    # Orchestrator Config
    orchestrator_type: str

    # Outline Tool Config
    outline_api_key: str
    outline_base_url: str
    outline_collection_id: str

    # Qdrant Tool Config
    qdrant_host: str
    qdrant_grpc_port: int
    qdrant_http_port: int

    class Config:
        # This tells pydantic-settings to load variables from a .env file if it exists
        # which is useful for local development.
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Pydantic-settings is case-insensitive by default, which is fine.
