import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise IT Support RAG Assistant API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = ""
    
    # Path to ChromaDB persistent vector store directory
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", os.path.join(os.path.dirname(__file__), "..", "..", "data", "vector_store"))
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "langchain")
    
    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    
    # Retrieval settings
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "4"))
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
