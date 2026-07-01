from typing import List
from langchain_core.documents import Document
from config.settings import TOP_K
from vectorstore.qdrant_manager import QdrantManager
from rag.embeddings import EmbeddingManager
from memory.session import SessionManager
from utils.logger import logger

class RAGRetriever:
    """
    Handles similarity search and retrieval operations from the session-isolated Qdrant collection.
    """
    
    def __init__(self) -> None:
        self.qdrant_manager = QdrantManager()

    def retrieve(self, query: str) -> List[Document]:
        """
        Perform similarity search on Qdrant and return matching chunks.
        """
        collection_name = SessionManager.get_qdrant_collection_name()
        
        if not self.qdrant_manager.collection_exists(collection_name):
            logger.warning(f"Collection '{collection_name}' does not exist. Returning empty context.")
            return []
            
        try:
            embeddings = EmbeddingManager.get_embeddings()
            vector_store = self.qdrant_manager.get_vector_store(collection_name, embeddings)
            
            logger.info(f"Retrieving top {TOP_K} matches from Qdrant for query: '{query}'")
            # QdrantVectorStore's similarity_search returns List[Document]
            docs = vector_store.similarity_search(query, k=TOP_K)
            logger.info(f"Successfully retrieved {len(docs)} documents.")
            return docs
        except Exception as e:
            logger.error(f"Error during Qdrant similarity search: {str(e)}")
            raise RuntimeError(f"RAG retrieval operation failed: {str(e)}")
