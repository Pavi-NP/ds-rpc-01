import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "resources" / "data"

class Settings:
    PROJECT_NAME: str = "Fintech RAG Assistant"
    API_VERSION: str = "v1"
    
    # Paths
    DATA_PATH: Path = DATA_DIR
    VECTOR_STORE_PATH: Path = BASE_DIR / "vector_store"
    CHROMA_PATH: Path = BASE_DIR / "chroma_db"
    
    # Model settings
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")  # "gemini-pro" if you're using Gemini elsewhere

# Singleton instance for import
settings = Settings()
