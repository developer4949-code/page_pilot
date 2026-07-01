from typing import Tuple, List, Generator
from memory.chat_memory import ChatMemory
from llm.factory import LLMFactory
from rag.retriever import RAGRetriever
from rag.prompt_builder import PromptBuilder
from langchain_core.documents import Document
from utils.logger import logger

class ChatService:
    """
    Orchestrates the retrieval of context, construction of prompts, 
    streaming of LLM answers, and conversation metadata updates.
    """
    
    def __init__(self) -> None:
        self.llm = LLMFactory.create()
        self.retriever = RAGRetriever()

    def query_rag(self, query: str) -> Tuple[List[Document], Generator[str, None, None]]:
        """
        Query the RAG pipeline by fetching matching documents and returning the LLM stream.
        
        Args:
            query: User's prompt.
            
        Returns:
            Tuple of (List of matched LangChain Documents, Token Generator stream).
        """
        logger.info(f"Querying RAG for: '{query}'")
        
        # 1. Similarity search matching current session
        context_docs = self.retriever.retrieve(query)
        
        # 2. Get chat history from current active conversation
        history = ChatMemory.to_llm_messages()
        
        # 3. Construct prompt incorporating instructions, context, history, and query
        messages = PromptBuilder.build_messages(
            query=query,
            context_docs=context_docs,
            history=history
        )
        
        # 4. Stream token responses
        stream_generator = self.llm.stream(messages)
        
        return context_docs, stream_generator

    def rename_conversation_if_needed(self, query: str) -> None:
        """
        Inspect current conversation message history. If it is the first exchange, 
        trigger a quick completion task to rename the conversation dynamically.
        """
        active_conv = ChatMemory.get_active_conversation()
        
        # Rename only if there is exactly 1 user message (first question)
        user_msg_count = sum(1 for m in active_conv.messages if m.role == "user")
        
        if user_msg_count == 1:
            logger.info(f"Attempting to generate automatic title for conversation: {active_conv.id}")
            title = self.generate_title(query)
            active_conv.title = title
            logger.info(f"Conversation {active_conv.id} auto-titled to '{title}'")

    def generate_title(self, query: str) -> str:
        """
        Use the LLM to generate a concise, 3-4 word title for the chat thread based on query.
        """
        prompt = [
            {
                "role": "system",
                "content": "You are a precise title generator. Create a short title (3-4 words max) summarizing the user's question. Do not use quotes, punctuation, or helper text. Return ONLY the title text."
            },
            {
                "role": "user",
                "content": query
            }
        ]
        try:
            title = ""
            for chunk in self.llm.stream(prompt):
                title += chunk
            cleaned_title = title.strip().strip('"').strip("'").strip()
            # If the response was empty or too long, truncate or fallback
            if not cleaned_title:
                return "Chat"
            if len(cleaned_title) > 40:
                cleaned_title = cleaned_title[:37] + "..."
            return cleaned_title
        except Exception as e:
            logger.error(f"Failed to generate conversation title: {str(e)}")
            return "Chat"