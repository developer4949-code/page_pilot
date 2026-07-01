from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid


@dataclass
class ChatMessage:
    role: str
    content: str

    timestamp: datetime = field(default_factory=datetime.utcnow)

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    sources: list[dict[str, Any]] = field(default_factory=list)

    token_usage: dict[str, Any] = field(default_factory=dict)