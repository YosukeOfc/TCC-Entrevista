"""
core/cached_data.py
Leituras do data.json com @st.cache_data (invalida automaticamente via mtime).
Use este módulo nas páginas de UI; writes continuam em core.persistence.
"""
import streamlit as st

from core.persistence import (
    carregar_historico as _carregar_historico,
    carregar_pendencias as _carregar_pendencias,
    get_file_mtime,
)


@st.cache_data(show_spinner=False)
def _historico_cached(user_id: str, mtime: float) -> list:
    return _carregar_historico(user_id)


@st.cache_data(show_spinner=False)
def _pendencias_cached(user_id: str, mtime: float) -> dict:
    return _carregar_pendencias(user_id)


def carregar_historico(user_id: str) -> list:
    if not user_id:
        return []
    return _historico_cached(user_id, get_file_mtime())


def carregar_pendencias(user_id: str) -> dict:
    if not user_id:
        return {}
    return _pendencias_cached(user_id, get_file_mtime())
