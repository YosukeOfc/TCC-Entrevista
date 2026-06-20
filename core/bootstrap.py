"""
core/bootstrap.py
Inicialização pesada com cache do Streamlit (CSS, Gemini).
"""
import os

import streamlit as st

from config.settings import CSS_PATH
from services import gemini_service


_FONT_CSS = (
    "*, body, html { font-family: 'Segoe UI', 'Source Sans 3', "
    "system-ui, -apple-system, sans-serif !important; }"
)


@st.cache_data(show_spinner=False)
def carregar_css(_mtime: float) -> str:
    try:
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            return " ".join(line for line in f.read().splitlines() if line.strip())
    except FileNotFoundError:
        return _FONT_CSS


def injetar_css() -> None:
    try:
        mtime = os.path.getmtime(CSS_PATH)
    except OSError:
        mtime = 0.0
    css = carregar_css(mtime)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def init_gemini(api_key: str) -> bool:
    gemini_service.init_client(api_key)
    return True
