# =============================================================================
# controllers/ProcessController.py — Document Loading & Chunking Controller
# =============================================================================
# PURPOSE:
#   The "Dirty Hands" phase. This controller is responsible for:
#     1. Loading raw files from disk (PDF or plain text)
#     2. Splitting them into overlapping text chunks
#     3. Returning the chunks ready for MongoDB insertion
#
# CALLED BY: routes/data.py → POST /api/data/process/{project_id}
#
# CHUNKING STRATEGY (must be documented in the Tech Report):
#   - chunk_size  = 500 tokens (characters as proxy)
#       Why 500? Large enough to contain a complete thought / paragraph.
#       Smaller chunks lose context; larger chunks reduce retrieval precision.
#   - chunk_overlap = 50 tokens
#       Why 50? Ensures sentences split across chunk boundaries appear in both
#       chunks, so a query hitting that sentence retrieves relevant context.
#   - Splitter: RecursiveCharacterTextSplitter
#       Tries to split on paragraphs → sentences → words → characters,
#       preserving semantic boundaries wherever possible.
#
# ARABIC PREPROCESSING (Bonus +10%):
#   Arabic text extracted from PDFs often has reversed characters and broken
#   ligatures. arabic-reshaper fixes the ligatures; python-bidi fixes the
#   display order. Both must run BEFORE chunking.
#
# TEAM NOTE (Pair A — Member 3):
#   This file carries 20% of the total rubric grade. Write clear comments
#   explaining why you chose these parameters.
# =============================================================================

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
    """
    Loads documents and splits them into overlapping text chunks.
    """

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
            return reshaped  # ← شيل get_display
        except Exception as e:
            print(f"⚠️ Arabic preprocessing failed: {e}")
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

        print("🔥 PROCESS STARTED")
        print("📁 Project:", project_id)
        print("📄 File:", filename)

        docs = self.get_file_content(project_id, filename)

        print(f"📄 Docs loaded: {len(docs)}")

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

        print(f"✂️ Chunks created: {len(chunks)}")

        result = []

        for i, chunk in enumerate(chunks):
            result.append({
                "chunk_text": chunk.page_content,
                "chunk_metadata": chunk.metadata,
                "chunk_order": i
            })

        print("✅ PROCESS DONE")

        return result