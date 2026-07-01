import os
from typing import List
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from langchain_qdrant import QdrantVectorStore
from utils.logger import logger

load_dotenv()

class QdrantManager:
    """
    Manages the lifecycle of Qdrant Cloud collections and vector stores.
    """
    
    def __init__(self) -> None:
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        
        if not self.url or not self.api_key:
            logger.error("Missing Qdrant credentials in environment variables.")
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in your .env file.")
        
        try:
            logger.info("Initializing Qdrant client connection.")
            self.client = QdrantClient(url=self.url, api_key=self.api_key)
            # Perform a quick ping to verify credentials
            self.client.get_collections()
            logger.info("Successfully connected to Qdrant Cloud.")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant Cloud: {str(e)}")
            raise RuntimeError(f"Qdrant connection error: {str(e)}")

    def check_health(self) -> bool:
        """
        Check if the Qdrant connection is active.
        """
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {str(e)}")
            return False

    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists in Qdrant.
        """
        try:
            collections = self.client.get_collections().collections
            names = [c.name for c in collections]
            return collection_name in names
        except Exception as e:
            logger.error(f"Error checking collection existence for '{collection_name}': {str(e)}")
            return False

    def create_collection(self, collection_name: str, vector_size: int = 384) -> bool:
        """
        Create a new collection if it does not already exist.
        """
        try:
            if self.collection_exists(collection_name):
                logger.info(f"Collection '{collection_name}' already exists.")
                return True

            logger.info(f"Creating Qdrant collection '{collection_name}' with vector size {vector_size}...")
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size,
                    distance=qmodels.Distance.COSINE
                )
            )
            logger.info(f"Collection '{collection_name}' created successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection '{collection_name}': {str(e)}")
            raise RuntimeError(f"Failed to create Qdrant collection: {str(e)}")

    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection from Qdrant.
        """
        try:
            if not self.collection_exists(collection_name):
                logger.warning(f"Attempted to delete collection '{collection_name}' but it does not exist.")
                return True

            logger.info(f"Deleting collection '{collection_name}'...")
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' deleted successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {str(e)}")
            return False

    def get_vector_store(self, collection_name: str, embeddings) -> QdrantVectorStore:
        """
        Get a LangChain QdrantVectorStore instance.
        """
        return QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=embeddings
        )
