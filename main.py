"""
main.py  ← entrypoint do Streamlit
Execute com: streamlit run main.py

Responsabilidades deste arquivo (e APENAS estas):
  1. Configurar a página (set_page_config — deve ser a 1ª chamada)
  2. Inicializar o cliente Gemini
  3. Injetar o CSS global
  4. Inicializar o estado da sessão
  5. Renderizar a sidebar
  6. Rotear para a página correta
"""
import streamlit as st

# ── 1. Page config (DEVE ser a primeira chamada Streamlit) ────
st.set_page_config(
    page_title="InterviewAI — Preparação Pro",
    page_icon="💼",
    layout="wide",
)

# ── 2. CSS + Gemini (cacheados entre reruns) ──────────────────
from config.settings import get_api_key
from core.bootstrap import injetar_css, init_gemini

injetar_css()

api_key = get_api_key()
if api_key:
    try:
        init_gemini(api_key)
    except Exception as e:
        st.error(f"Erro ao inicializar Gemini: {e}")

# ── 3. Inicializar session_state ──────────────────────────────
from core.state import init_state, is_authenticated
init_state()

# ── 4. Autenticação ───────────────────────────────────────────
if not is_authenticated():
    from ui.pages import auth
    auth.render()
    st.stop()

# ── 5. Sidebar ────────────────────────────────────────────────
from ui.sidebar import render_sidebar
render_sidebar()

# ── 6. Roteamento de páginas (imports lazy) ───────────────────
from core.state import get_fase, get_pagina

pagina = get_pagina()

if pagina == "historico":
    from ui.pages import historico
    historico.render()

elif pagina == "dashboard":
    from ui.pages import dashboard
    dashboard.render()

elif pagina == "pendencias":
    from ui.pages import pendencias
    pendencias.render()

else:
    fase = get_fase()
    if fase == "selecao":
        from ui.pages import selecao
        selecao.render()
    elif fase == "confirmacao":
        from ui.pages import confirmacao
        confirmacao.render()
    elif fase == "entrevista":
        from ui.pages import entrevista
        entrevista.render()
    elif fase == "relatorio":
        from ui.pages import relatorio
        relatorio.render()
