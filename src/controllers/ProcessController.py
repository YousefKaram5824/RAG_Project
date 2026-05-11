import os
from typing import List
from controllers.BaseController import BaseController
from controllers.FileController import FileController
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
import os
import arabic_reshaper
from bidi.algorithm import get_display
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langdetect import detect


class ProcessController(BaseController):

    def __init__(self):
        super().__init__()  
        self.file_controller = FileController()
###########################
# uosef wrote this function
###########################
    def get_file_content(self, project_id: str, filename: str):

        file_path = self.file_controller.get_file_path(project_id, filename)

        if filename.endswith(".pdf"):
            docs = PyMuPDFLoader(file_path).load()

        elif filename.endswith(".txt"):
            docs = TextLoader(file_path, encoding="utf-8").load()

        else:
            raise ValueError("Unsupported file type")

        return docs
###########################
# uosef wrote this function
###########################
    def preprocess_arabic(self, text: str) -> str:
        try:
            reshaped = arabic_reshaper.reshape(text)
            return reshaped
        except Exception as e:
            print(f"Arabic preprocessing failed: {e}")
            return text
    
    def is_arabic(self, text: str) -> bool:
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        return arabic_chars > len(text) * 0.3
###########################
# uosef wrote this function
###########################

    def process_files(
    self,
    project_id: str,
    filename: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[dict]:

        print("PROCESS STARTED")
        print("Project:", project_id)
        print("File:", filename)

        docs = self.get_file_content(project_id, filename)

        print(f"Docs loaded: {len(docs)}")

        # optional Arabic preprocessing
        # Arabic gate — only preprocess Arabic documents
        for doc in docs:
            if doc.page_content:
                if self.is_arabic(doc.page_content):
                    doc.page_content = self.preprocess_arabic(doc.page_content)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap
        )

        chunks = splitter.split_documents(docs)

        print(f"Chunks created: {len(chunks)}")

        result = []

        for i, chunk in enumerate(chunks):
            result.append({
                "chunk_text": chunk.page_content,
                "chunk_metadata": chunk.metadata,
                "chunk_order": i
            })

        print("PROCESS DONE")

        return result