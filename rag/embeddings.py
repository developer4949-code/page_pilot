from langchain_huggingface import HuggingFaceEmbeddings
from config.settings import EMBEDDING_MODEL
from utils.logger import logger

class EmbeddingManager:
    """
    Singleton class to manage the initialization of the embedding model.
    """
    _instance = None

    @classmethod
    def get_embeddings(cls) -> HuggingFaceEmbeddings:
        """
        Retrieve the singleton instance of HuggingFaceEmbeddings.
        
        Loads the model configured in EMBEDDING_MODEL if not already loaded.
        """
        if cls._instance is None:
            logger.info(f"Initializing embedding model: {EMBEDDING_MODEL} (Lazy Load)")
            try:
                cls._instance = HuggingFaceEmbeddings(
                    model_name=EMBEDDING_MODEL,
                    encode_kwargs={"normalize_embeddings": True}
                )
                logger.info("Embedding model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize HuggingFaceEmbeddings: {str(e)}")
                raise RuntimeError(f"Error loading embedding model {EMBEDDING_MODEL}: {str(e)}")
        return cls._instance
