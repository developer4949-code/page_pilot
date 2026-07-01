# pyrefly: ignore [missing-import]
import streamlit as st
from config.settings import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE,
)
from memory.session import SessionManager
from ui.sidebar import render_sidebar
from ui.chat import render_chat
from ui.components import render_header

# Initialize Session state and generate UUIDs
SessionManager.initialize()

# Configure Streamlit page parameters
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE,
)

# Apply global premium CSS stylesheets
with open("assets/style.css") as css:
    st.markdown(
        f"<style>{css.read()}</style>",
        unsafe_allow_html=True,
    )

# Render UI Layers
render_sidebar()
render_header()
render_chat()