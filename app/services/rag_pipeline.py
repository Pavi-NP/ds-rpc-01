from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

from app.vector_store import load_vector_store
from app.config import settings

# Load vector store and initialize LLM
vector_store = load_vector_store()
llm = ChatOpenAI(model_name=settings.MODEL_NAME)

# Create a RetrievalQA chain with source document return enabled
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_store.as_retriever(),
    return_source_documents=True
)

def get_insight(query: str) -> dict:
    """
    Run the RAG chain on a given query and return the answer and sources.
    """
    result = rag_chain({"query": query})
    return {
        "answer": result["result"],
        "source_documents": [
            doc.metadata.get("source", "unknown") 
            for doc in result.get("source_documents", [])
        ]
    }
