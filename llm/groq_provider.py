import os
from typing import Generator, List, Dict, Any
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from llm.provider import BaseLLM
from config.settings import (
    GROQ_MODEL,
    TEMPERATURE,
)

load_dotenv()


class GroqProvider(BaseLLM):

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing. Please set it in your environment or .env file.")

        self.llm = ChatGroq(
            api_key=api_key,
            model=GROQ_MODEL,
            temperature=TEMPERATURE,
        )

    def stream(self, messages: List[Dict[str, Any]]) -> Generator[str, None, None]:
        try:
            for chunk in self.llm.stream(messages):
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve stream from Groq LLM: {str(e)}")