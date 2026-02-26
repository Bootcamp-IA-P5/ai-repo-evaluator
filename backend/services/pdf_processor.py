import logging
import os
import re

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


logger = logging.getLogger(__name__)

class BriefingProcessor:
    """
    Class responsible for processing the project briefing PDF.
    It extracts and chunks text to be used as RAG context.
    """
    
    def __init__(self, file_path: str, chunk_size: int = 1000, chunk_overlap: int = 150):
        """
        Initializes the processor with the path to the uploaded PDF file.
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.lower().endswith(".pdf"):
            raise ValueError(f"The file is not a PDF: {file_path}")

        self.file_path = file_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _clean_text(self, text: str) -> str:
        """
        Cleans extra spaces and empty lines from extracted text.
        """
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

    def process(self) -> list[dict]:
        """
        Runs text extraction, cleaning, and chunking.
        """
        try:
            # Ingestion: Load the briefing PDF
            loader = PyPDFLoader(self.file_path)
            pages = loader.load()

            if not pages:
                logger.warning("The PDF does not contain text pages.")
                return []

            # Consolidation: Merge all pages to preserve cross-page context
            full_text = " ".join([p.page_content for p in pages])
            full_text = self._clean_text(full_text)
            
            # Chunking:
            # The briefing describes required student deliverables.
            # Overlap helps avoid splitting requirements at hard boundaries.
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ".", " "]
            )
            
            chunks = text_splitter.split_text(full_text)
            
            # RAG structuring:
            # Build document objects with metadata for traceability.
            documents = [
                {
                    "page_content": chunk,
                    "metadata": {
                        "source": "project_briefing",
                        "type": "requirement",
                        "chunk_index": i
                    }
                }
                for i, chunk in enumerate(chunks)
            ]

            logger.info(f"Briefing processed: {len(documents)} chunks generated.")
            
            return documents

        except Exception as e:
            logger.error(f"Critical error processing the briefing PDF: {e}")
            raise
