# ds-rpc-01/app/services/rag_service.py

import os
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter

# NOTE: You need to have OPENAI_API_KEY in your environment variables
# (e.g., in a .env file) for this to work.

class RAGService:
    def __init__(self):
        # Initialize models - these are loaded once
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        self.chain = load_qa_chain(self.llm, chain_type="stuff")

    def query(self, question: str, accessible_files: list[str]):
        """
        Answers a question based on a user's accessible documents.
        """
        if not accessible_files:
            return "You do not have access to any documents. Please contact your administrator."

        try:
            # 1. Load documents
            docs = []
            for file_path in accessible_files:
                loader = UnstructuredFileLoader(file_path)
                docs.extend(loader.load())

            # 2. Split documents into chunks
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            texts = text_splitter.split_documents(docs)

            # 3. Create a role-specific vector store in memory
            docsearch = FAISS.from_documents(texts, self.embeddings)

            # 4. Find relevant documents and run the QA chain
            relevant_docs = docsearch.similarity_search(question)
            response = self.chain.run(input_documents=relevant_docs, question=question)
            
            return response

        except Exception as e:
            print(f"An error occurred in the RAG service: {e}")
            return "Sorry, I encountered an error while processing your request."

# Create a single instance to be used by the app
rag_service = RAGService()
