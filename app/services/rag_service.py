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
        return self.vector_store.similarity_search(question, user_role)

    async def _prepare_context(self, documents: List[Any]) -> str:
        return "\n".join([doc.page_content for doc in documents])


    async def _generate_response(self, question: str, context: str, user_role: str, user_context: Dict[str, Any]) -> str:
        prompt = (
            f"User Role: {user_role}\n"
            f"User Question: {question}\n"
            f"Relevant Sources:\n{context}\n"
            "Based on the above sources, provide a detailed answer."
        )
        response_obj = await self.llm.ainvoke(prompt)
        return response_obj.content  # ✅ this is the correct way

    async def _prepare_sources(self, documents: List[Any]) -> List[Dict[str, str]]:
        return [
            {
                "filename": doc.metadata.get("source", "unknown"),
                "summary": doc.page_content[:200]  # Or more sophisticated summary logic
            }
            for doc in documents
        ]


    async def cleanup(self):
        """Cleanup resources if needed."""
        logger.info("Cleaning up RAG service resources.")

# Create a singleton instance
rag_service = RagService()

