from dataclasses import dataclass, field
from typing import List
import uuid
from models.chat_message import ChatMessage

@dataclass
class Conversation:
    """
    Model representing a distinct conversation thread.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    messages: List[ChatMessage] = field(default_factory=list)
