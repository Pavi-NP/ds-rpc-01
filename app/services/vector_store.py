from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from app.config import settings

def load_vector_store():
    """
    Load the Chroma vector store using OpenAI embeddings and the configured path.
    """
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(
        persist_directory=str(settings.CHROMA_PATH),
        embedding_function=embeddings
    )
    return vector_store
