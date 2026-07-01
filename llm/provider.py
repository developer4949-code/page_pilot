from abc import ABC, abstractmethod
from typing import Generator, List, Dict, Any


class BaseLLM(ABC):
    """Abstract interface for every LLM provider."""

    @abstractmethod
    def stream(self, messages: List[Dict[str, Any]]) -> Generator[str, None, None]:
        """Yield streamed response chunks."""
        pass