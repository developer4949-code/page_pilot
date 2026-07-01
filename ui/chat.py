"""
Chat UI.

This module is responsible ONLY for rendering the chat interface.
"""

import streamlit as st
from memory.chat_memory import ChatMemory
from services.chat_service import ChatService
from ui.components import render_citations

# Instantiate the service orchestrator
chat_service = ChatService()

def render_chat() -> None:
    """
    Render the complete chat interface including history, inputs, streams, and references.
    """
    # Initialize chat memory
    ChatMemory.initialize()

    # Render all historic messages for the active conversation
    for msg_idx, message in enumerate(ChatMemory.all()):
        with st.chat_message(message.role):
            st.markdown(message.content)
            # Display citation expandable widget for assistant messages if present
            if message.role == "assistant" and message.sources:
                render_citations(message.sources, namespace=f"hist_{msg_idx}")

    # Accept user query input
    prompt = st.chat_input(
        placeholder="Ask anything about your documents..."
    )

    if not prompt:
        return

    # Add and render user query immediately
    ChatMemory.add(role="user", content=prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Stream the assistant's RAG response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        response = ""
        
        # Retrieve context vectors and initiate LLM completion stream
        with st.spinner("Searching documents & drafting response..."):
            try:
                context_docs, stream_generator = chat_service.query_rag(prompt)
            except Exception as e:
                st.error(f"Failed to query knowledge base: {str(e)}")
                return

        # Stream LLM tokens to interface
        try:
            for token in stream_generator:
                response += token
                placeholder.markdown(response + "▌")
            # Remove stream cursor character
            placeholder.markdown(response)
        except Exception as stream_error:
            st.error(f"Stream interrupted: {str(stream_error)}")
            return
            
        # Format citations metadata array
        sources_list = []
        for doc in context_docs:
            sources_list.append({
                "filename": doc.metadata.get("filename", "document.pdf"),
                "page": doc.metadata.get("page", "?"),
                "chunk": doc.metadata.get("chunk", "?"),
                "text": doc.page_content
            })
            
        # Display the expandable sources container with unique namespace
        render_citations(sources_list, namespace="live")

    # Save Assistant response and metadata to session memory
    ChatMemory.add(
        role="assistant",
        content=response,
        sources=sources_list
    )

    # Rename conversation if it is the first exchange
    chat_service.rename_conversation_if_needed(prompt)
    
    # Refresh to update conversation list sidebar titles
    st.rerun()