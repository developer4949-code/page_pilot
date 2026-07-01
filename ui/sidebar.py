import streamlit as st
from config.settings import (
    GROQ_MODEL,
    EMBEDDING_MODEL,
)
from memory.session import SessionManager
from memory.chat_memory import ChatMemory
from services.ingestion_service import IngestionService
from vectorstore.qdrant_manager import QdrantManager
from utils.file_utils import clean_session_temp_dir

# Initialize services
ingestion_service = IngestionService()

def render_sidebar() -> None:
    """
    Renders the sidebar interface containing file uploads, conversations history,
    configuration details, and database connectivity metrics.
    """
    with st.sidebar:
        st.title("🚀 PagePilot")
        st.caption("AI-Powered RAG Chat Platform")
        st.divider()

        # ---------------------------------------------
        # Chat Controls (New Chat, Clear Chat)
        # ---------------------------------------------
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ New Chat", use_container_width=True, help="Create a empty conversation thread"):
                ChatMemory.create_new_conversation()
                st.rerun()
        with col2:
            if st.button("🧹 Clear Chat", use_container_width=True, help="Clear active conversation messages"):
                ChatMemory.clear()
                st.rerun()

        st.divider()

        # ---------------------------------------------
        # File Uploader & Document Ingestion
        # ---------------------------------------------
        st.subheader("Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            key="pdf_uploader",
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            # Filter out files that are already uploaded to prevent redundant processing
            new_uploads = []
            for f in uploaded_files:
                # Validate extension and file size (max 10MB)
                from services.upload_service import UploadService
                is_valid, err_msg = UploadService.validate_file(f.name, f.size)
                if not is_valid:
                    st.error(err_msg)
                    continue

                already_ingested = any(doc.filename == f.name for doc in st.session_state.uploaded_documents)
                if not already_ingested:
                    new_uploads.append(f)

            
            if new_uploads:
                with st.spinner("Ingesting and embedding PDFs..."):
                    try:
                        ingested = ingestion_service.ingest_files(new_uploads)
                        if ingested:
                            st.toast(f"Successfully loaded: {', '.join(ingested)}", icon="✅")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Ingestion failed: {str(e)}")

        # Display currently uploaded files list
        if st.session_state.uploaded_documents:
            st.markdown("**Processed Documents:**")
            for doc in st.session_state.uploaded_documents:
                size_kb = doc.file_size / 1024
                st.markdown(f"<span style='font-size:0.85rem; color:#94a3b8;'>📄 {doc.filename} ({size_kb:.1f} KB)</span>", unsafe_allow_html=True)
            
            # Action to Delete all Documents (Wipes collection and clears temp directories)
            if st.button("🗑 Delete All Documents", use_container_width=True, type="secondary"):
                with st.spinner("Clearing vectors and temp files..."):
                    try:
                        # Deleting dynamic session collection from Qdrant
                        q_mgr = QdrantManager()
                        q_mgr.delete_collection(SessionManager.get_qdrant_collection_name())
                        
                        # Empty local temp storage
                        clean_session_temp_dir(SessionManager.get_session_id())
                        
                        # Reset session metadata & current messages
                        st.session_state.uploaded_documents = []
                        ChatMemory.clear()
                        st.toast("System cleared successfully!", icon="🧹")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Failed to clear resources: {str(ex)}")

        st.divider()

        # ---------------------------------------------
        # Multi-Conversation History List
        # ---------------------------------------------
        st.subheader("Chat Threads")
        ChatMemory.initialize()
        conversations = st.session_state.conversations
        active_id = st.session_state.active_conversation_id
        
        if conversations:
            for conv_id, conv in list(conversations.items()):
                # Highlight active conversation
                is_active = (conv_id == active_id)
                button_style = "primary" if is_active else "secondary"
                label = f"💬 {conv.title}"
                
                col_btn, col_del = st.columns([6, 1])
                with col_btn:
                    if st.button(label, key=f"select_conv_{conv_id}", use_container_width=True, type=button_style):
                        ChatMemory.switch_conversation(conv_id)
                        st.rerun()
                with col_del:
                    if st.button("❌", key=f"del_conv_{conv_id}", help="Delete chat"):
                        ChatMemory.delete_conversation(conv_id)
                        st.rerun()
        else:
            st.caption("No recent conversations.")

        st.divider()

        # ---------------------------------------------
        # System Health & configuration parameters
        # ---------------------------------------------
        st.subheader("System Status")
        try:
            q_health = QdrantManager().check_health()
            if q_health:
                st.success("🟢 Qdrant Cloud: Active")
            else:
                st.error("🔴 Qdrant Cloud: Offline")
        except Exception:
            st.error("🔴 Qdrant Cloud: Unconfigured")
            
        st.markdown(
            f"<div class='config-card'>"
            f"<div class='config-label'>LLM Model:</div><div class='config-val'>{GROQ_MODEL}</div>"
            f"<div class='config-label' style='margin-top:6px;'>Embedding:</div><div class='config-val'>{EMBEDDING_MODEL}</div>"
            f"<div class='config-label' style='margin-top:6px;'>Session ID:</div><div class='config-val' style='font-size:0.75rem;'>{SessionManager.get_session_id()[:8]}...</div>"
            f"</div>",
            unsafe_allow_html=True
        )