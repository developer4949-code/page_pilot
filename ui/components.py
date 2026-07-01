import streamlit as st
from typing import List, Dict, Any

def render_header() -> None:
    """
    Renders the app's top header banner.
    """
    st.markdown(
        "<h1 style='text-align: center; margin-bottom: 0px;'>🤖 PagePilot</h1>"
        "<p style='text-align: center; color: #94a3b8; font-size: 1.1rem; margin-top: 5px; margin-bottom: 30px;'>"
        "Your Premium AI RAG Knowledge Assistant. Upload PDFs and start chatting."
        "</p>",
        unsafe_allow_html=True
    )

def render_citations(sources: List[Dict[str, Any]], namespace: str = "0") -> None:
    """
    Renders an interactive Streamlit expander containing matched context chunks
    with reference citations, serving as 'clickable' sources.
    
    Args:
        sources: List of source metadata dicts with filename, page, chunk, text.
        namespace: A unique string prefix to avoid duplicate widget keys when
                   this function is called multiple times (e.g. per message index).
    """
    if not sources:
        return
        
    with st.expander("📚 Retrieved Citations & Sources", expanded=False):
        for idx, src in enumerate(sources):
            filename = src.get("filename", "document.pdf")
            page = src.get("page", "?")
            chunk = src.get("chunk", "?")
            text = src.get("text", "")
            
            st.markdown(
                f"<div style='border-bottom: 1px solid #1f2937; padding-bottom: 10px; margin-bottom: 10px;'>"
                f"<span style='color: #3b82f6; font-weight: 600;'>[{idx + 1}] {filename}</span> "
                f"<span style='color: #6b7280; font-size: 0.85rem;'> (Page {page}, Chunk {chunk})</span>"
                f"</div>",
                unsafe_allow_html=True
            )
            st.text_area(
                label=f"Content excerpt for {filename} Page {page}",
                value=text,
                height=110,
                key=f"cite_text_{namespace}_{filename}_{idx}",
                disabled=True
            )