from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP
from utils.logger import logger

class DocumentSplitter:
    """
    Handles chunking of document texts into smaller segments using RecursiveCharacterTextSplitter.
    """
    
    @staticmethod
    def split_documents(documents: List[Document]) -> List[Document]:
        """
        Split a list of LangChain documents into smaller semantic chunks.
        """
        logger.info(f"Initializing text splitter: chunk_size={CHUNK_SIZE}, chunk_overlap={CHUNK_OVERLAP}")
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                length_function=len
            )
            chunks = splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} page(s) into {len(chunks)} chunk(s).")
            return chunks
        except Exception as e:
            logger.error(f"Error during text splitting: {str(e)}")
            raise RuntimeError(f"Document text splitting failed: {str(e)}")
