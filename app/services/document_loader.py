#ds-rpc-01/app/services/document_loader.py

import os
import logging
from typing import List, Dict
from pathlib import Path
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class DocumentLoader:
    def __init__(self, resources_path: str = "./resources/data"):
        self.resources_path = Path(resources_path)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50
        )

    def load_all_documents(self) -> Dict[str, List[Document]]:
        department_docs = {}
        for department_dir in self.resources_path.iterdir():
            if department_dir.is_dir():
                department_name = department_dir.name
                logger.info(f"Loading documents for {department_name}")
                docs = self._load_department_documents(department_dir, department_name)
                if docs:
                    department_docs[department_name] = docs
                    logger.info(f"Loaded {len(docs)} chunks for {department_name}")
        return department_docs

    def _load_department_documents(self, dept_path: Path, department: str) -> List[Document]:
        documents = []
        for file_path in dept_path.rglob("*"):
            if file_path.is_file():
                docs = self._load_single_file(file_path, department)
                if docs:
                    documents.extend(docs)
                    logger.info(f"Loaded {file_path.name}: {len(docs)} chunks")
        return documents

    def _load_single_file(self, file_path: Path, department: str) -> List[Document]:
        extension = file_path.suffix.lower()
        loader = {
            '.pdf': PyPDFLoader,
            '.txt': TextLoader,
            '.md': TextLoader,
            '.csv': self._load_csv_file,
            '.docx': Docx2txtLoader,
            '.doc': Docx2txtLoader
        }.get(extension)

        if loader:
            try:
                if extension == '.csv':
                    return loader(file_path, department)
                raw_docs = loader(str(file_path)).load()
                split_docs = self.text_splitter.split_documents(raw_docs)
                for doc in split_docs:
                    doc.metadata.update({
                        'department': department,
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'file_type': extension
                    })
                return split_docs
            except Exception as e:
                logger.error(f"Error loading file {file_path}: {e}")
                return []
        else:
            logger.warning(f"Unsupported file type: {extension}")
            return []

    def _load_csv_file(self, file_path: Path, department: str) -> List[Document]:
        try:
            df = pd.read_csv(file_path, low_memory=False)
            documents = []

            summary_text = (
                f"CSV Summary for {file_path.name}:\n"
                f"Number of rows: {len(df)}\n"
                f"Columns: {', '.join(df.columns)}\n\n"
            )
            documents.append(Document(
                page_content=summary_text,
                metadata={
                    'department': department,
                    'filename': file_path.name,
                    'file_path': str(file_path),
                    'file_type': '.csv',
                    'content_type': 'summary'
                }
            ))

            chunk_size = max(1, len(df) // 40)
            for start in range(0, len(df), chunk_size):
                end = start + chunk_size
                chunk_df = df.iloc[start:end]
                chunk_text = f"Data Chunk (rows {start + 1}-{end}) from {file_path.name}:\n{chunk_df.to_string(index=False)}"
                documents.append(Document(
                    page_content=chunk_text,
                    metadata={
                        'department': department,
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'file_type': '.csv',
                        'content_type': 'data_chunk',
                        'chunk_start': start,
                        'chunk_end': end
                    }
                ))
            return documents
        except Exception as e:
            logger.error(f"Error processing CSV {file_path}: {e}")
            return []

# Optional: test code
# if __name__ == "__main__":
#     loader = DocumentLoader()
#     docs = loader.load_all_documents()
#     print(f"Loaded {len(docs)} documents.")




# import os
# import logging
# from typing import List, Dict
# from pathlib import Path
# import pandas as pd
# from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_core.documents import Document


# logger = logging.getLogger(__name__)

# class DocumentLoader:
#     """
#     Loads and processes documents from a structured directory.
#     Supports PDF, TXT, MD, CSV, DOC, and DOCX files.
#     Splits documents into manageable chunks for downstream processing.
#     """

#     def __init__(self, resources_path: str = "./resources/data"):
#         self.resources_path = Path(resources_path)
#         self.text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=300,
#             chunk_overlap=50,
#             length_function=len,
#             separators=["\n\n", "\n", " ", ""]
#         )

#     def load_all_documents(self) -> Dict[str, List[Document]]:
#         """
#         Loads and organizes documents from all department subdirectories.
#         Returns:
#             Dict[str, List[Document]]: Mapping of department name to list of document chunks.
#         """
#         department_docs = {}
#         for department_dir in self.resources_path.iterdir():
#             if department_dir.is_dir():
#                 department_name = department_dir.name
#                 logger.info(f"Loading documents for {department_name}")
#                 docs = self._load_department_documents(department_dir, department_name)
#                 if docs:
#                     department_docs[department_name] = docs
#                     logger.info(f"Loaded {len(docs)} chunks for {department_name}")
#         return department_docs


#     def _load_department_documents(self, dept_path: Path, department: str) -> List[Document]:
#         """
#         Loads all supported documents from a specific department folder.
#         """
#         documents = []
#         for file_path in dept_path.rglob("*"):
#             if file_path.is_file():
#                 try:
#                     docs = self._load_single_file(file_path, department)
#                     if docs:
#                         documents.extend(docs)
#                         logger.info(f"Loaded {file_path.name}: {len(docs)} chunks")
#                 except Exception as e:
#                     logger.error(f"Error loading {file_path}: {e}")
#         return documents


#     def _load_single_file(self, file_path: Path, department: str) -> List[Document]:
#         """
#         Loads and splits a single file based on its extension.
#         """
#         extension = file_path.suffix.lower()
#         try:
#             if extension == '.pdf':
#                 loader = PyPDFLoader(str(file_path))
#             elif extension in ['.txt', '.md']:
#                 loader = TextLoader(str(file_path), encoding='utf-8')
#             elif extension == '.csv':
#                 return self._load_csv_file(file_path, department)
#             elif extension in ['.docx', '.doc']:
#                 loader = Docx2txtLoader(str(file_path))
#             else:
#                 logger.warning(f"Unsupported file type: {extension}")
#                 return []

#             raw_docs = loader.load()
#             split_docs = self.text_splitter.split_documents(raw_docs)

#             # Add metadata to each chunk
#             for doc in split_docs:
#                 doc.metadata.update({
#                     'department': department,
#                     'filename': file_path.name,
#                     'file_path': str(file_path),
#                     'file_type': extension
#                 })

#             return split_docs

#         except Exception as e:
#             logger.error(f"Error loading file {file_path}: {e}")
#             return []



#     def _load_csv_file(self, file_path: Path, department: str) -> List[Document]:
#         """
#         Efficiently processes and chunks a CSV file.
#         Returns a summary document and data chunks.
#         """
#         try:
#             df = pd.read_csv(file_path, low_memory=False)
#             documents = []

#             # Create a summary document
#             summary_text = (
#                 f"CSV Summary for {file_path.name}:\n"
#                 f"Number of rows: {len(df)}\n"
#                 f"Columns: {', '.join(df.columns)}\n\n"
#             )
#             for col in df.columns:
#                 sample_vals = df[col].dropna().astype(str).unique()[:3]
#                 summary_text += f"{col} example values: {', '.join(sample_vals)}\n"
#             documents.append(Document(
#                 page_content=summary_text,
#                 metadata={
#                     'department': department,
#                     'filename': file_path.name,
#                     'file_path': str(file_path),
#                     'file_type': '.csv',
#                     'content_type': 'summary'
#                 }
#             ))

#             # Chunk the CSV rows
#             chunk_size = 40 if len(df) > 100 else len(df)
#             for start in range(0, len(df), chunk_size):
#                 end = min(start + chunk_size, len(df))
#                 chunk_df = df.iloc[start:end]
#                 chunk_text = f"Data Chunk (rows {start+1}-{end}) from {file_path.name}:\n"
#                 chunk_text += chunk_df.to_string(index=False)

#                 documents.append(Document(
#                     page_content=chunk_text,
#                     metadata={
#                         'department': department,
#                         'filename': file_path.name,
#                         'file_path': str(file_path),
#                         'file_type': '.csv',
#                         'content_type': 'data_chunk',
#                         'chunk_start': start,
#                         'chunk_end': end
#                     }
#                 ))

#             return documents

#         except Exception as e:
#             logger.error(f"Error processing CSV {file_path}: {e}")
#             return []

# document_loader = DocumentLoader()