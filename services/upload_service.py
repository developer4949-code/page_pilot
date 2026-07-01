import os
import time
import shutil
from typing import Tuple
import config.settings as settings
from utils.logger import logger
from vectorstore.qdrant_manager import QdrantManager

class UploadService:
    """
    Validates uploaded file size/format and performs automated periodic cleanup of expired session resources.
    """
    
    MAX_FILE_SIZE_MB = 10  # 10 MB limits
    ALLOWED_EXTENSIONS = {".pdf"}

    @staticmethod
    def validate_file(filename: str, size_bytes: int) -> Tuple[bool, str]:
        """
        Validate if the file extension is allowed and does not exceed file size limits.
        
        Returns:
            Tuple: (is_valid: bool, error_message: str)
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext not in UploadService.ALLOWED_EXTENSIONS:
            return False, f"File format '{ext}' is not supported. Only PDF documents are allowed."

        max_allowed_bytes = UploadService.MAX_FILE_SIZE_MB * 1024 * 1024
        if size_bytes > max_allowed_bytes:
            return False, f"File '{filename}' exceeds maximum allowed size of {UploadService.MAX_FILE_SIZE_MB}MB."

        return True, ""

    @staticmethod
    def run_garbage_collector() -> None:
        """
        Locate and clean up temporary storage folders and Qdrant collections older than 24 hours.
        """
        if not os.path.exists(settings.TEMP_DIR_ROOT):
            return

        logger.info("Initializing garbage collection sweep.")
        now = time.time()
        expiry_duration_seconds = 24 * 60 * 60  # 24 hours

        try:
            qdrant_mgr = QdrantManager()
        except Exception as e:
            logger.error(f"Garbage collector aborted: failed to connect to Qdrant: {str(e)}")
            return

        for item in os.listdir(settings.TEMP_DIR_ROOT):
            item_path = os.path.join(settings.TEMP_DIR_ROOT, item)

            if not os.path.isdir(item_path):
                continue

            # Verify folder age
            folder_mod_time = os.path.getmtime(item_path)
            if (now - folder_mod_time) > expiry_duration_seconds:
                logger.info(f"Expired session resource found: '{item}'. Initiating purge.")
                
                # Dynamic collection naming formula
                collection_name = f"session_{item.replace('-', '')}"
                
                # 1. Drop vector database collection
                try:
                    if qdrant_mgr.collection_exists(collection_name):
                        qdrant_mgr.delete_collection(collection_name)
                        logger.info(f"Dropped vector collection: '{collection_name}'")
                except Exception as q_error:
                    logger.error(f"Failed to drop collection '{collection_name}': {str(q_error)}")

                # 2. Delete temporary directory
                try:
                    shutil.rmtree(item_path)
                    logger.info(f"Deleted temporary directory: '{item_path}'")
                except Exception as folder_error:
                    logger.error(f"Failed to delete directory '{item_path}': {str(folder_error)}")
