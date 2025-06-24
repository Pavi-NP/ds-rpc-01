# ds-rpc-01/app/services/vector_store.py

import logging
from typing import List, Dict, Optional
from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from chromadb.config import Settings
from typing import List
from langchain.schema import Document

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Manages vector stores for document retrieval using OpenAI embeddings and ChromaDB."""
    
    def __init__(self, openai_api_key: str):
        self.openai_api_key = openai_api_key
        
        self.embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        self.chroma_settings = Settings(anonymized_telemetry=False)
        self.department_stores: Dict[str, Chroma] = {}
        self.global_store: Optional[Chroma] = None

    def create_global_store(self, split_docs: List[Document]) -> None:
        """Create a global vector store containing all documents."""
        try:
            self.global_store = Chroma(
                collection_name="global_company_data",
                embedding_function=self.embeddings,
                client_settings=self.chroma_settings
            )
            self.global_store.add_documents(split_docs)
            
            logger.info(f"Global vector store created with {len(split_docs)} documents")
        except Exception as e:
            logger.error(f"Error creating global store: {e}")

    def create_department_stores(self, department_docs: Dict[str, List[Document]]):
        """Create department-specific vector stores."""
        logger.info("Creating department-specific vector stores...")
        for department, documents in department_docs.items():
            if documents:
                try:
                    store = Chroma(
                        collection_name=f"dept_{department.lower().replace('-', '_')}",
                        embedding_function=self.embeddings,
                        
                        client_settings=self.chroma_settings
                    )
                    store.add_documents(documents)
                    
                    self.department_stores[department] = store
                    logger.info(f"Vector store created for {department}: {len(documents)} documents")
                except Exception as e:
                    logger.error(f"Error creating vector store for {department}: {e}")

    def get_retriever(self, user_role: str, departments: Optional[List[str]] = None):
        """Return a retriever based on user role and departments."""
        if user_role == "c-level" and self.global_store:
            return self.global_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 5, "score_threshold": 0.3})

        accessible_depts = departments or ["general"]
        if len(accessible_depts) == 1 and accessible_depts[0] in self.department_stores:
            return self.department_stores[accessible_depts[0]].as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 5, "score_threshold": 0.3})

        if self.global_store:
            return self.global_store.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"k": 5, "score_threshold": 0.3, "filter": {"department": {"$in": accessible_depts}}}
            )
        return None

    def similarity_search(self, query: str, user_role: str) -> List[Document]:
        """Perform a similarity search using the appropriate retriever for the user's role."""
        retriever = self.get_retriever(user_role)
        if retriever:
            try:
                return retriever.get_relevant_documents(query)
            except Exception as e:
                logger.error(f"Error in similarity search: {e}")
        return []

