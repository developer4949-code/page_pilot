"""
Global configuration for PagePilot.
Only constants should live here.
"""

APP_NAME = "PagePilot"
APP_TAGLINE = "Your AI Knowledge Assistant"

PAGE_TITLE = "PagePilot"
PAGE_ICON = "🚀"

LAYOUT = "wide"

INITIAL_SIDEBAR_STATE = "expanded"

LLM_PROVIDER = "groq"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

VECTOR_DB = "Qdrant Cloud"

DEFAULT_SYSTEM_MESSAGE = (
    "Welcome to PagePilot!\n\n"
    "Upload your PDF documents and start chatting with them."
)

GROQ_MODEL = "llama-3.3-70b-versatile"

TEMPERATURE = 0.2

MAX_TOKENS = 2048

STREAMING = True

# RAG Configurations
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 5

# Path and Vector Configurations
COLLECTION_PREFIX = "session"
TEMP_DIR_ROOT = "temp"