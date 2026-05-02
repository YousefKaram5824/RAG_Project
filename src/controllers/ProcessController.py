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


class ProcessController(BaseController):
    """
    Loads documents and splits them into overlapping text chunks.
    """

    def __init__(self):
        super().__init__()
        self.file_controller = FileController()

    def get_file_content(self, project_id: str, filename: str):
        """
        Loads raw file content using the appropriate LangChain loader.
        Supports: .pdf (PyMuPDFLoader) and .txt (TextLoader)

        Args:
            project_id: The project folder name
            filename:   The file to load (e.g. "resume.pdf")

        Returns:
            List of LangChain Document objects (each has .page_content + .metadata)

        TODO (Pair A):
            1. Get the file path from self.file_controller.get_file_path(...)
            2. Check the file extension
            3. For .pdf  → use PyMuPDFLoader(file_path).load()
            4. For .txt  → use TextLoader(file_path, encoding="utf-8").load()
            5. If Arabic content is detected → apply preprocess_arabic() first
            6. Return the list of Document objects
        """
        # TODO: implement file loading
        pass

    def preprocess_arabic(self, text: str) -> str:
        """
        Fixes Arabic text extracted from PDFs so it chunks correctly.

        Arabic in PDFs is often stored in visual order (right-to-left characters
        reversed) with broken ligatures. Two libraries fix this:
          - arabic_reshaper: reconnects Arabic letter forms (ligatures)
          - bidi.algorithm: restores the correct RTL reading order

        Args:
            text: Raw Arabic text string from PyMuPDF

        Returns:
            Properly ordered and reshaped Arabic text, ready for chunking

        TODO (Pair A — Member 3, Arabic Bonus):
            import arabic_reshaper
            from bidi.algorithm import get_display
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        """
        # TODO: implement Arabic preprocessing
        pass

    def process_files(
        self,
        project_id: str,
        filename: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[dict]:
        """
        Main entry point. Loads the file and splits it into chunks.

        Args:
            project_id: Project folder name
            filename:   File to process
            chunk_size: Target chunk size in characters (default 500)
            overlap:    Overlap between consecutive chunks in characters (default 50)

        Returns:
            List of dicts, each dict has:
              {
                "chunk_text":     str,   # the text content
                "chunk_metadata": dict,  # {"source": filename, "page": int, ...}
                "chunk_order":    int    # sequential index (0, 1, 2, ...)
              }

        TODO (Pair A):
            1. Call self.get_file_content(project_id, filename)
            2. Create RecursiveCharacterTextSplitter(
                   chunk_size=chunk_size,
                   chunk_overlap=overlap
               )
            3. Call splitter.split_documents(docs) to get chunks
            4. Map each chunk to the dict format above
            5. Return the list
        """
        # TODO: implement chunking pipeline
        pass
