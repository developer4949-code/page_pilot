from dataclasses import dataclass
from datetime import datetime

@dataclass
class UploadedDocument:
    """
    Model representing metadata of an uploaded and ingested document.
    """
    filename: str
    file_hash: str
    file_size: int
    upload_time: datetime
