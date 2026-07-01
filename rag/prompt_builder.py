from typing import List, Dict, Any
from langchain_core.documents import Document

class PromptBuilder:
    """
    Constructs structured messages for Chat LLMs, combining system prompts, contexts, history, and questions.
    """
    
    @staticmethod
    def build_messages(
        query: str,
        context_docs: List[Document],
        history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Combine system instruction, retrieved context, conversation history, and current question into LLM messages.
        
        Args:
            query: The user's latest query.
            context_docs: Relevant document chunks retrieved from Qdrant.
            history: List of previous messages in the conversation (role: content).
            
        Returns:
            List of message dictionaries ready for ChatGroq provider.
        """
        # Format context chunks with clear metadata dividers
        context_chunks = []
        if context_docs:
            for doc in context_docs:
                source = doc.metadata.get("filename", "Unknown Document")
                page = doc.metadata.get("page", "?")
                chunk_id = doc.metadata.get("chunk", "?")
                context_chunks.append(
                    f"[Source: {source}, Page: {page}, Chunk: {chunk_id}]\n{doc.page_content}"
                )
            context_text = "\n\n---\n\n".join(context_chunks)
        else:
            context_text = "No document context is available. Let the user know they need to upload documents to search them."

        # Define system instruction
        system_content = (
            "You are PagePilot, a premium AI knowledge assistant designed to analyze and chat with PDF documents.\n"
            "Answer the user's question using only the context chunks provided below. Keep answers precise, readable, and structured.\n"
            "When citing facts from the text, append citations in the format [DocumentName, Page X] (e.g. [Specification.pdf, Page 3]).\n"
            "If the retrieved context does not contain enough information to answer the query, state that the information is not present in the uploaded documents. Do not hallucinate.\n\n"
            f"--- START RETRIEVED CONTEXT ---\n{context_text}\n--- END RETRIEVED CONTEXT ---"
        )

        messages = [
            {"role": "system", "content": system_content}
        ]

        # Add history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add user's question
        messages.append({
            "role": "user",
            "content": query
        })

        return messages
