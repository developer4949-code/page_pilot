import streamlit as st
from typing import List, Dict, Any
from models.chat_message import ChatMessage
from models.conversation import Conversation
from config.settings import DEFAULT_SYSTEM_MESSAGE
import uuid
from datetime import datetime

class ChatMemory:
    """
    Manages multiple conversations and chat messages in Streamlit's session state.
    """

    @staticmethod
    def initialize() -> None:
        """
        Initialize active conversation and conversation directory in session state.
        """
        if "conversations" not in st.session_state:
            st.session_state.conversations = {}

        if "active_conversation_id" not in st.session_state or not st.session_state.active_conversation_id:
            if not st.session_state.conversations:
                ChatMemory.create_new_conversation()
            else:
                st.session_state.active_conversation_id = list(st.session_state.conversations.keys())[0]

    @staticmethod
    def create_new_conversation() -> str:
        """
        Create a new conversation thread, append a welcome message, and set it as active.
        """
        if "conversations" not in st.session_state:
            st.session_state.conversations = {}
            
        new_id = str(uuid.uuid4())
        new_conv = Conversation(
            id=new_id,
            title="New Chat",
            messages=[
                ChatMessage(
                    role="assistant",
                    content=DEFAULT_SYSTEM_MESSAGE,
                    message_id="welcome"
                )
            ]
        )
        st.session_state.conversations[new_id] = new_conv
        st.session_state.active_conversation_id = new_id
        return new_id

    @staticmethod
    def get_active_conversation() -> Conversation:
        """
        Get the active conversation instance.
        """
        ChatMemory.initialize()
        active_id = st.session_state.active_conversation_id
        return st.session_state.conversations[active_id]

    @staticmethod
    def switch_conversation(conversation_id: str) -> None:
        """
        Switch the active conversation to the specified ID.
        """
        if conversation_id in st.session_state.conversations:
            st.session_state.active_conversation_id = conversation_id

    @staticmethod
    def delete_conversation(conversation_id: str) -> None:
        """
        Delete a conversation thread. Switch active if the deleted thread was active.
        """
        if conversation_id in st.session_state.conversations:
            del st.session_state.conversations[conversation_id]
            
        # Adjust active conversation if the deleted one was current
        if st.session_state.active_conversation_id == conversation_id:
            st.session_state.active_conversation_id = None
            ChatMemory.initialize()

    @staticmethod
    def add(role: str, content: str, sources: List[Dict[str, Any]] = None, token_usage: Dict[str, Any] = None) -> ChatMessage:
        """
        Add a new chat message to the currently active conversation.
        """
        active_conv = ChatMemory.get_active_conversation()
        msg = ChatMessage(
            role=role,
            content=content,
            message_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            sources=sources or [],
            token_usage=token_usage or {}
        )
        active_conv.messages.append(msg)
        return msg

    @staticmethod
    def all() -> List[ChatMessage]:
        """
        Get all messages belonging to the active conversation.
        """
        active_conv = ChatMemory.get_active_conversation()
        return active_conv.messages

    @staticmethod
    def clear() -> None:
        """
        Clear all messages in the active conversation, leaving only the welcome message.
        """
        active_conv = ChatMemory.get_active_conversation()
        active_conv.messages = [
            ChatMessage(
                role="assistant",
                content=DEFAULT_SYSTEM_MESSAGE,
                message_id="welcome"
            )
        ]

    @staticmethod
    def to_llm_messages() -> List[Dict[str, str]]:
        """
        Format the message history (excluding welcome message) for the LLM providers.
        """
        history = []
        for msg in ChatMemory.all():
            if msg.message_id == "welcome":
                continue
            history.append({
                "role": msg.role,
                "content": msg.content
            })
        return history