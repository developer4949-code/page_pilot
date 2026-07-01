import os
# pyrefly: ignore [missing-import]
import streamlit as st
from datetime import datetime
from typing import List
from utils.file_utils import get_session_temp_dir, calculate_sha256
from utils.logger import logger
from models.uploaded_document import UploadedDocument
from memory.session import SessionManager
from rag.document_processor import DocumentProcessor
from rag.splitter import DocumentSplitter
from rag.embeddings import EmbeddingManager
from vectorstore.qdrant_manager import QdrantManager

class IngestionService:
    """
    Coordinates PDF loader, splitter, and vector database operations to ingest documents.
    """
    
    def __init__(self) -> None:
        self.qdrant_manager = QdrantManager()

    def ingest_files(self, uploaded_files: List[st.runtime.uploaded_file_manager.UploadedFile]) -> List[str]:
        """
        Ingest uploaded files into the session Qdrant collection.
        
        Args:
            uploaded_files: List of Streamlit UploadedFile objects.
            
        Returns:
            List of successfully ingested filenames.
        """
        session_id = SessionManager.get_session_id()
        collection_name = SessionManager.get_qdrant_collection_name()
        
        # Ensure session collection is created in Qdrant (Dimension is 384 for all-MiniLM-L6-v2)
        self.qdrant_manager.create_collection(collection_name=collection_name, vector_size=384)
        
        temp_dir = get_session_temp_dir(session_id)
        ingested_filenames = []
        
        for uploaded_file in uploaded_files:
            filename = uploaded_file.name
            
            # Read bytes to compute hash and write to file
            file_bytes = uploaded_file.getvalue()
            file_hash = calculate_sha256(file_bytes)
            
            # Check duplicate hash within current session
            is_duplicate = False
            for doc in st.session_state.uploaded_documents:
                if doc.file_hash == file_hash:
                    logger.warning(f"File '{filename}' is a duplicate of already uploaded document: {doc.filename}")
                    is_duplicate = True
                    break
            
            if is_duplicate:
                # We skip duplicate files
                continue

            # Write file to temporary folder
            temp_file_path = os.path.join(temp_dir, filename)
            try:
                with open(temp_file_path, "wb") as f:
                    f.write(file_bytes)
                
                # Load PDF content
                pages = DocumentProcessor.load_pdf(temp_file_path)
                
                # Chunk content
                chunks = DocumentSplitter.split_documents(pages)
                
                # Decorate chunks with metadata required for payloads/citations
                upload_time = datetime.utcnow()
                upload_time_str = upload_time.isoformat()
                for idx, chunk in enumerate(chunks):
                    chunk.metadata["filename"] = filename
                    chunk.metadata["source"] = filename
                    # Ensure pages are 1-indexed
                    chunk.metadata["page"] = chunk.metadata.get("page", 0) + 1
                    chunk.metadata["chunk"] = idx
                    chunk.metadata["session"] = session_id
                    chunk.metadata["upload_time"] = upload_time_str
                
                # Retrieve singleton Embeddings
                embeddings = EmbeddingManager.get_embeddings()
                
                # Get dynamic LangChain QdrantVectorStore wrapper
                vector_store = self.qdrant_manager.get_vector_store(collection_name, embeddings)
                
                # Ingest to Qdrant Cloud
                logger.info(f"Upserting {len(chunks)} chunks for '{filename}' into collection '{collection_name}'...")
                vector_store.add_documents(chunks)
                logger.info(f"Ingested '{filename}' into Qdrant.")
                
                # Track document in session
                doc_metadata = UploadedDocument(
                    filename=filename,
                    file_hash=file_hash,
                    file_size=len(file_bytes),
                    upload_time=upload_time
                )
                st.session_state.uploaded_documents.append(doc_metadata)
                ingested_filenames.append(filename)
                
            except Exception as e:
                logger.error(f"Failed to ingest file '{filename}': {str(e)}")
                raise RuntimeError(f"Ingestion failed for '{filename}': {str(e)}")
                
            finally:
                # Cleanup temp file immediately
                if os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                        logger.info(f"Deleted temporary file: {temp_file_path}")
                    except Exception as cleanup_error:
                        logger.error(f"Failed to delete temp file '{temp_file_path}': {str(cleanup_error)}")
                        
        return ingested_filenames
