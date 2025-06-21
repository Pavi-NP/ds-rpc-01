# ds-rpc-01/app/services/rag_service.py

import os
import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from . import document_loader
from app.services.vector_store import VectorStoreService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RagService:
    """Retrieval-Augmented Generation (RAG) service for processing queries using OpenAI's language model."""

    def __init__(self, model_name="gpt-3.5-turbo", temperature=0):
        self.document_loader = document_loader.DocumentLoader()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")
        self.persist_directory = None
        self.initialized = False
        
        # Initialize the language model and embeddings
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.embeddings = OpenAIEmbeddings(api_key=self.api_key)
        self.vector_store = VectorStoreService(openai_api_key=self.api_key)

    async def initialize(self, persist_directory: str= None):
        self.persist_directory = persist_directory
        self.initialized = True
        await self.load_and_create_vector_stores()

    async def load_and_create_vector_stores(self):
        """Load documents from resources and create vector stores."""
        logger.info("🔄 Starting document loading and vector store creation...")

        try:
            department_docs = self.document_loader.load_all_documents()
            if not department_docs:
                logger.warning("⚠️ No documents found in the resources folder.")
                return

            logger.info(f"📁 Loaded documents for {len(department_docs)} departments.")
            self.vector_store.create_department_stores(department_docs)

            all_docs = [doc for docs in department_docs.values() for doc in docs]
            if all_docs:
                self.vector_store.create_global_store(all_docs)
                logger.info(f"✅ Created global vector store with {len(all_docs)} total documents.")
            else:
                logger.warning("⚠️ No documents available to create a global vector store.")
        except Exception as e:
            logger.error(f"❌ Error during document loading: {e}")

    async def query(self, question: str, user_role: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a user query using RAG with detailed features."""
        if not self.initialized:
            raise RuntimeError("RAG service not initialized")

        try:
            relevant_docs = await self.retrieve_relevant_documents(question, user_role)
            if not relevant_docs:
                return {
                    "response": "I couldn't find relevant information for your query.",
                    "sources": [],
                    "confidence": 0.0,
                }

            context = await self._prepare_context(relevant_docs)
            response = await self._generate_response(question, context, user_role, user_context)
            sources = await self._prepare_sources(relevant_docs)

            return {
                "response": response,
                "sources": sources,
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": f"An error occurred: {str(e)}",
                "sources": [],
            }

    async def retrieve_relevant_documents(self, question: str, user_role: str) -> List[str]:
        """Retrieve relevant documents based on the user's question and role."""
        return await self.vector_store.similarity_search(question, user_role)

    async def _prepare_context(self, documents: List[str]) -> str:
        """Prepare context string from documents."""
        return "\n".join(documents)

    async def _generate_response(self, question: str, context: str, user_role: str, user_context: Dict[str, Any]) -> str:
        """Generate a response using the language model."""
        prompt = (
            f"User Role: {user_role}\n"
            f"User Question: {question}\n"
            f"Relevant Sources:\n{context}\n"
            "Based on the above sources, provide a detailed answer."
        )
        response_obj = await self.llm.acall(prompt)
        return response_obj.get("choices", [{}])[0].get("message", {}).get("content", "")

    async def _prepare_sources(self, documents: List[str]) -> List[Dict[str, str]]:
        """Format sources for response."""
        return [{"source": doc} for doc in documents]

    async def cleanup(self):
        """Cleanup resources if needed."""
        logger.info("Cleaning up RAG service resources.")

# Create a singleton instance
rag_service = RagService()





# # ds-rpc-02/app/services/rag_service.py

# import os
# import logging
# from typing import Dict, Any, List
# from langchain_openai import ChatOpenAI
# from . import document_loader
# from app.services.vector_store import VectorStoreService

# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# class RagService:
#     """
#     Retrieval-Augmented Generation (RAG) service for processing queries using 
#     OpenAI's language model and managing document retrieval.
#     """

#     def __init__(self, model_name="gpt-3.5-turbo", temperature=0):
#         self.document_loader = document_loader.DocumentLoader()
#         self.api_key = None
#         self.initialized = False
#         self.llm = ChatOpenAI(model=model_name, temperature=temperature)
#         self.vector_store = VectorStoreService(openai_api_key=os.getenv("OPENAI_API_KEY"))

#     async def initialize(self, openai_api_key: str, persist_directory: str):
#         self.api_key = openai_api_key
#         self.persist_directory = persist_directory
#         self.initialized = True
#         await self.load_and_create_vector_stores()

#     async def load_and_create_vector_stores(self):
#         """Load documents from resources and create vector stores."""
#         logger.info("🔄 Starting document loading and vector store creation...")

#         try:
#             # Load all department documents
#             department_docs = self.document_loader.load_all_documents()
#             if not department_docs:
#                 logger.warning("⚠️ No documents found in the resources folder.")
#                 return

#             logger.info(f"📁 Loaded documents for {len(department_docs)} departments.")
#             self.vector_store.create_department_stores(department_docs)

#             # Combine all docs for global store
#             all_docs = [doc for docs in department_docs.values() for doc in docs]
#             if all_docs:
#                 self.vector_store.create_global_store(all_docs)
#                 logger.info(f"✅ Created global vector store with {len(all_docs)} total documents.")
#             else:
#                 logger.warning("⚠️ No documents available to create a global vector store.")
                
#         except Exception as e:
#             logger.error(f"❌ Error during document loading: {e}")

#     async def query(self, question: str, user_role: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
#         """Process a user query using RAG with detailed features."""
#         if not self.initialized:
#             raise RuntimeError("RAG service not initialized")

#         try:
#             relevant_docs = await self.retrieve_relevant_documents(question, user_role)
#             if not relevant_docs:
#                 return {
#                     "response": "I couldn't find relevant information for your query.",
#                     "sources": [],
#                     "confidence": 0.0,
#                 }

#             context = self._prepare_context(relevant_docs)
#             response = await self._generate_response(question, context, user_role, user_context)
#             sources = self._prepare_sources(relevant_docs)

#             return {
#                 "response": response,
#                 "sources": sources,
#             }
#         except Exception as e:
#             logger.error(f"Error processing query: {e}")
#             return {
#                 "response": f"An error occurred: {str(e)}",
#                 "sources": [],
#             }

#     async def retrieve_relevant_documents(self, question: str, user_role: str) -> List[str]:
#         """Retrieve relevant documents based on the user's question and role."""
#         if user_role == "c-level":
#             return await self.vector_store.similarity_search(question, user_role)
#         else:
#             return await self.vector_store.similarity_search(question, user_role)

#     async def _prepare_context(self, documents: List[str]) -> str:
#         """Prepare context string from documents."""
#         return "\n".join(documents)

#     async def _generate_response(self, question: str, context: str, user_role: str, user_context: Dict[str, Any]) -> str:
#         """Generate a response using the language model."""
#         prompt = (
#             f"User Role: {user_role}\n"
#             f"User Question: {question}\n"
#             f"Relevant Sources:\n{context}\n"
#             "Based on the above sources, provide a detailed answer."
#         )
#         response_obj = await self.llm.acall(prompt)
#         return response_obj.get("choices", [{}])[0].get("message", {}).get("content", "")

#     async def _prepare_sources(self, documents: List[str]) -> List[Dict[str, str]]:
#         """Format sources for response."""
#         return [{"source": doc} for doc in documents]

#     async def cleanup(self):
#         """Cleanup resources if needed."""
#         logger.info("Cleaning up RAG service resources.")

# # Create a singleton instance
# rag_service = RagService()

# import os
# import logging
# from typing import Dict, Any, List
# from langchain_openai import ChatOpenAI  # Import the language model
# from langchain.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# from langchain.prompts import ChatPromptTemplate
# from operator import itemgetter
# from langchain_openai import ChatOpenAI
# from langchain_core.output_parsers import StrOutputParser

# from ..services import document_loader
# from app.services.vector_store import VectorStoreService

# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)
 
# class RagService:
#     """
#     Retrieval-Augmented Generation (RAG) service for processing queries using 
#     OpenAI's language model and managing document retrieval.
#     """
    

#     def __init__(self, model_name="gpt-3.5-turbo", temperature=0):
#         self.document_loader = document_loader.DocumentLoader()
#         #self.vector_store = None
#         self.api_key = None
#         self.initialized = False
#         self.llm = ChatOpenAI(model=model_name, temperature=temperature)  # Initialize the language model
        
#         self.vector_store = VectorStoreService(openai_api_key=os.getenv("OPENAI_API_KEY"))
#     ...
#         #self.document_loader = document_loader.DocumentLoader()  # Placeholder for document loader
#         #self.vector_store = None  # Placeholder for vector store

# #     Retrieval-Augmented Generation (RAG) service for processing queries using 
# #     OpenAI's language model and managing document retrieval.
# #     """

    
#     async def initialize(self, openai_api_key: str,persist_directory: str ):
#         self.openai_api_key = openai_api_key
#         self.persist_directory = persist_directory
#         # Initialize your language model with the API key if needed
#         # For example, if ChatDeepAI accepts an api_key parameter, set it here
#         # self.llm.api_key = openai_api_key

#         self.initialized = True
#         # Optionally, load documents, create vector stores etc.
#         await self.load_and_create_vector_stores()
    
#     async def load_and_create_vector_stores(self):
#         """
#         Asynchronously load documents from resources and create vector stores 
#         (department-specific and global).
#         """
#         logger.info("🔄 Starting document loading and vector store creation...")

#         try:
#             # Step 1: Load all department documents
#             department_docs = self.document_loader.load_all_documents()
#             if not department_docs:
#                 logger.warning("⚠️ No documents found in the resources folder.")
#                 return

#             logger.info(f"📁 Loaded documents for {len(department_docs)} departments.")

#             # Step 2: Create department-level vector stores
#             self.vector_store.create_department_stores(department_docs)

#             if department_docs is None:
#                 # Initialize it or handle the error
#                 raise RuntimeError("some_object is not initialized properly")
#             else:
#                 department_docs.create_global_store()

#             # Step 3: Combine all docs for global store
#             all_docs = [doc for docs in department_docs.values() for doc in docs]
#             if all_docs:
#                 self.vector_store.create_global_store(all_docs)
#                 logger.info(f"✅ Created global vector store with {len(all_docs)} total documents.")
            
#             else:
#                 logger.warning("⚠️ No documents available to create a global vector store.")
            
#             if all_docs is None:
#                 # Initialize it or handle the error
#                 raise RuntimeError("some_object is not initialized properly")
#             else:
#                     all_docs.create_global_store()
            
#         except Exception as e:
#             logger.error(f"❌ Error during document loading: {e}")
            
#     async def query(self, question: str, user_role: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
#         """Process a user query using RAG with detailed features."""
#         if not self.initialized:
#             raise RuntimeError("RAG service not initialized")
        
#         try:
#             # Retrieve relevant documents
#             relevant_docs = await self.retrieve_relevant_documents(question, user_role)
#             if not relevant_docs:
#                 return {
#                     "response": "I couldn't find relevant information for your query.",
#                     "sources": [],
#                     "confidence": 0.0,
#                     "model_version": "gpt-3.5-turbo",
#                     "search_strategy": "semantic"
#                 }

#             # Prepare context string from retrieved documents
#             context = self._prepare_context(relevant_docs)

#             # Generate response using the language model
#             response = await self._generate_response(question, context, user_role, user_context)

#             # Format sources for transparency
#             sources = self._prepare_sources(relevant_docs)


#             return {
#                 "response": response,
#                 "sources": sources,
#                 "model_version": "gpt-3.5-turbo",
#                 "search_strategy": "semantic"
#             }
#         except Exception as e:
#             logger.error(f"Error processing query: {e}")
#             return {
#                 "response": f"An error occurred: {str(e)}",
#                 "sources": [],
#                 "model_version": "gpt-3.5-turbo",
#                 "search_strategy": "semantic"
#             }

#     async def retrieve_relevant_documents(self, question: str, user_role: str) -> List[str]:
#         """Retrieve relevant documents based on the user's question and role."""
#         if user_role == "c-level":
#             return await self.vector_store.similarity_search(question, user_role)
#         elif user_role in ["finance", "marketing", "hr", "engineering"]:
#             return await self.vector_store.similarity_search(question, user_role)
#         else:  # For employees or other roles
#             return await self.vector_store.similarity_search(question, "general")

#     async def _prepare_context(self, documents: List[str]) -> str:
#         """Prepare context string from documents."""
#         return "\n".join(documents)

#     async def _generate_response(self, question: str, context: str, user_role: str, user_context: Dict[str, Any]) -> str:
#         """Generate a response using the language model."""
#         prompt = (
#             f"User Role: {user_role}\n"
#             f"User Question: {question}\n"
#             f"Relevant Sources:\n{context}\n"
#             "Based on the above sources, provide a detailed answer."
#         )
#         response_obj = await self.llm.acall(prompt)
#         return response_obj.get("choices", [{}])[0].get("message", {}).get("content", "")

#     async def _prepare_sources(self, documents: List[str]) -> List[Dict[str, str]]:
#         """Format sources for response."""
#         return [{"source": doc} for doc in documents]

#     async def cleanup(self):
#         """Cleanup resources if needed."""
#         logger.info("Cleaning up RAG service resources.")

# # Create a singleton instance
# rag_service = RagService()

