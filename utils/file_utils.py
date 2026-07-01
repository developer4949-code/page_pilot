import os
import hashlib
import shutil
from typing import Union
import config.settings as settings
from utils.logger import logger

def get_session_temp_dir(session_id: str) -> str:
    """
    Get or create the temp directory path for a specific session.
    """
    session_dir = os.path.join(settings.TEMP_DIR_ROOT, session_id)
    os.makedirs(session_dir, exist_ok=True)
    return os.path.abspath(session_dir)

def calculate_sha256(content: bytes) -> str:
    """
    Calculate the SHA256 checksum of raw file bytes.
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(content)
    return sha256_hash.hexdigest()

def clean_session_temp_dir(session_id: str) -> None:
    """
    Safely delete the temp directory associated with a session.
    """
    session_dir = os.path.join(settings.TEMP_DIR_ROOT, session_id)
    if os.path.exists(session_dir):
        try:
            shutil.rmtree(session_dir)
            logger.info(f"Successfully cleaned up temporary directory for session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete temp directory {session_dir}: {str(e)}")
