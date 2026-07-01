import streamlit as st
import uuid


class SessionManager:

    @staticmethod
    def initialize() -> None:
        """
        Initialize the required Streamlit session state attributes.
        """
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())

        if "conversations" not in st.session_state:
            st.session_state.conversations = {}  # conversation_id -> Conversation

        if "active_conversation_id" not in st.session_state:
            st.session_state.active_conversation_id = None

        if "uploaded_documents" not in st.session_state:
            st.session_state.uploaded_documents = []  # List of UploadedDocument

        # Run garbage collection for expired sessions asynchronously on startup
        from services.upload_service import UploadService
        try:
            UploadService.run_garbage_collector()
        except Exception:
            pass


    @staticmethod
    def get_session_id() -> str:
        """
        Get the current session UUID.
        """
        if "session_id" not in st.session_state:
            SessionManager.initialize()
        return st.session_state.session_id

    @staticmethod
    def get_qdrant_collection_name() -> str:
        """
        Get the Qdrant collection name for the current session.
        """
        return f"session_{SessionManager.get_session_id().replace('-', '')}"