# # ds-rpc-01/app/services/vector_store.py

import logging
from typing import List, Dict, Optional
from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from chromadb.config import Settings

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

# #ds-rpc-02/app/services/vector_store.py
# import logging
# from typing import List, Dict, Any, Optional
# from langchain_community.vectorstores import Chroma
# from langchain_openai import OpenAIEmbeddings
# from langchain_core.documents import Document
# from chromadb.config import Settings
# from langchain_community.embeddings import DeepAIEmbeddings

# logger = logging.getLogger(__name__)



# class VectorStoreService:
#     """
#     Manages vector stores for document retrieval using OpenAI embeddings and ChromaDB.
#     Supports department-specific and global stores, with role-based retrieval.
#     """

#     def __init__(self, openai_api_key: str, persist_directory: str = "./chroma_db"):
#         self.openai_api_key = openai_api_key
#         self.persist_directory = persist_directory

#         # Initialize embedding model
#         self.embeddings = OpenAIEmbeddings(
#             openai_api_key=openai_api_key,
#             model="text-embedding-3-small"
#         )

#         # ChromaDB settings for persistence
#         self.chroma_settings = Settings(
#             persist_directory=persist_directory,
#             anonymized_telemetry=False
#         )

#         self.department_stores: Dict[str, Chroma] = {}
#         self.global_store: Optional[Chroma] = None

#         self.vector_store = Chroma(
#             persist_directory=self.persist_directory,
#             embedding_function=DeepAIEmbeddings(api_key=self.openai_api_key)
#         )



#     def create_global_store(self, split_docs: List[Document]) -> List[Document]:
#         """
#         Create and persist a global vector store containing all documents.
#         Intended for C-level access.
#         """
#         logger.info("Creating global vector store...")
#         try:
#             self.global_store = Chroma(
#                 collection_name="global_company_data",
#                 embedding_function=self.embeddings,
#                 persist_directory=self.persist_directory,
#                 client_settings=self.chroma_settings
#             )
#             self.global_store.add_documents(split_docs)
#             self.global_store.persist()
#             logger.info(f"Global vector store created: {len(split_docs)} documents")
#             return split_docs
#         except Exception as e:
#             logger.error(f"Error creating global vector store: {e}")
#             return []



#     def get_retriever(self, user_role: str, departments: List[str] = None):
#         """Return a retriever for the user's role."""
#         if user_role == "c-level" and self.global_store:
#             return self.global_store.as_retriever(
#                 search_type="similarity_score_threshold",
#                 search_kwargs={"k": 5, "score_threshold": 0.3}
#             )

#         # Map roles to departments
#         role_dept_mapping = {
#             "engineering": ["engineering"],
#             "marketing": ["marketing"],
#             "finance": ["finance"],
#             "hr": ["hr"],
#             "employee": ["general"]
#         }
#         accessible_depts = departments or role_dept_mapping.get(user_role, ["general"])

#         if len(accessible_depts) == 1 and accessible_depts[0] in self.department_stores:
#             return self.department_stores[accessible_depts[0]].as_retriever(
#                 search_type="similarity_score_threshold",
#                 search_kwargs={"k": 5, "score_threshold": 0.3}
#             )

#         if self.global_store:
#             return self.global_store.as_retriever(
#                 search_type="similarity_score_threshold",
#                 search_kwargs={
#                     "k": 5,
#                     "score_threshold": 0.3,
#                     "filter": {"department": {"$in": accessible_depts}}
#                 }
#             )
#         return None


#     def similarity_search(self, query: str, user_role: str, k: int = 5) -> List[Document]:
#         """
#         Perform a similarity search using the appropriate retriever for the user's role.
#         """
#         retriever = self.get_retriever(user_role)
#         if retriever:
#             try:
#                 return retriever.get_relevant_documents(query)
#             except Exception as e:
#                 logger.error(f"Error in similarity search: {e}")
#         return []


#     def create_department_stores(self, department_docs: Dict[str, List[Document]]):
#         """Create department-specific vector stores."""
#         logger.info("Creating department-specific vector stores...")
#         for department, documents in department_docs.items():
#             if documents:
#                 try:
#                     store = Chroma(
#                         collection_name=f"dept_{department.lower().replace('-', '_')}",
#                         embedding_function=self.embeddings,
#                         persist_directory=self.persist_directory,
#                         client_settings=self.chroma_settings
#                     )
#                     store.add_documents(documents)
#                     store.persist()
#                     self.department_stores[department] = store
#                     logger.info(f"Vector store created for {department}: {len(documents)} documents")
#                 except Exception as e:
#                     logger.error(f"Error creating vector store for {department}: {e}")


#     # def create_department_stores_csv(self, documents: List[Document]):
#     #     """
#     #     Create and persist a department-level vector store from CSV chunked documents.
#     #     """
#     #     logger.info("Creating department-level vector store from CSV documents...")
#     #     try:
#     #         self.department_store = Chroma(
#     #             collection_name="department_csv_data",
#     #             embedding_function=self.embeddings,
#     #             persist_directory=self.persist_directory,
#     #             client_settings=self.chroma_settings
#     #         )
#     #         self.department_store.add_documents(documents)
#     #         self.department_store.persist()
#     #         logger.info(f"Department vector store created with {len(documents)} documents.")
#     #     except Exception as e:
#     #         logger.error(f"Error creating department vector store: {e}")

#     def get_retriever_csv(self):
#         """
#         Return a retriever from the department-level CSV vector store.
#         """
#         if self.department_store:
#             return self.department_store.as_retriever(
#                 search_type="similarity_score_threshold",
#                 search_kwargs={"k": 5, "score_threshold": 0.3}
#             )
#         else:
#             logger.warning("Department CSV vector store is not initialized.")
#             return None


#     def similarity_search_csv(self, query: str, k: int = 5) -> List[Document]:
#         """
#         Perform a similarity search on the department-level CSV vector store.
#         """
#         retriever = self.get_retriever_csv()
#         if retriever:
#             try:
#                 return retriever.get_relevant_documents(query)
#             except Exception as e:
#                 logger.error(f"Error in CSV similarity search: {e}")
#         return []
