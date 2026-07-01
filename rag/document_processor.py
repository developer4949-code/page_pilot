from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from utils.logger import logger

class DocumentProcessor:
    """
    Handles file parsing and loading using LangChain document loaders.
    """
    
    @staticmethod
    def load_pdf(file_path: str) -> List[Document]:
        """
        Load and parse a PDF file into LangChain Document pages.
        """
        logger.info(f"Attempting to load PDF from path: {file_path}")
        try:
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            logger.info(f"PDF loading completed. Extracted {len(pages)} page(s).")
            return pages
        except Exception as e:
            logger.error(f"Error parsing PDF file {file_path}: {str(e)}")
            raise RuntimeError(f"Failed to parse PDF document: {str(e)}")
