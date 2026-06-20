"""
ui/sidebar.py
Renderiza a sidebar com as 3 páginas de navegação e o progresso da entrevista.
"""
import streamlit as st

import core.state as state
from core.bootstrap import init_gemini
from services import gemini_service


def render_sidebar() -> None:
    with st.sidebar:
        _logo()
        _progresso_entrevista()
        _navegacao()
        _respostas_atuais()
        _spacer()
        _btn_nova_sessao()
        _aviso_api_key_sidebar()
        _rodape()


# ─── Componentes internos ─────────────────────────────────────

def _logo() -> None:
    st.markdown(
        """
        <div style="padding:16px 0 24px; border-bottom:1px solid rgba(255,255,255,0.08);
                    margin-bottom:16px;">
          <div style="font-size:20px; font-weight:700; color:#fff;
                      letter-spacing:-0.5px;">💼 InterviewAI</div>
          <div style="font-size:11px; color:#888; margin-top:3px;">Preparação Pro</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _progresso_entrevista() -> None:
    if state.get_fase() != "entrevista" or not state.get_session_id():
        return
    n_resp = state.count_respostas()
    max_total = state.get_max_perguntas()
    pct    = n_resp / max_total if max_total else 0
    info   = state.get_info_pergunta_atual()
    st.markdown(
        f"""
        <div style="background:rgba(0,96,171,0.25); border-radius:8px;
                    padding:14px 16px; margin-bottom:16px;
                    border-left:3px solid #0060ab;">
          <div style="font-size:11px; color:#aaa; text-transform:uppercase;
                      letter-spacing:0.05em;">Progresso — {info['bloco_label']}</div>
          <div style="font-size:15px; font-weight:600; color:#fff; margin-top:4px;">
            Questão {min(n_resp+1, max_total)} de {max_total}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(pct)
    st.markdown("<br>", unsafe_allow_html=True)


def _navegacao() -> None:
    st.markdown(
        '<div style="font-size:10px; font-weight:700; color:#666; '
        'text-transform:uppercase; letter-spacing:0.1em; '
        'margin-bottom:6px; padding-left:4px;">Menu</div>',
        unsafe_allow_html=True,
    )
    pagina = state.get_pagina()
    _nav_btn("🎤  Iniciar Entrevista", "entrevista", pagina == "entrevista")
    _nav_btn("⏳  Pendências",          "pendencias",  pagina == "pendencias")
    _nav_btn("📋  Histórico",          "historico",  pagina == "historico")
    _nav_btn("📊  Dashboard",          "dashboard",  pagina == "dashboard")


def _nav_btn(label: str, key: str, ativo: bool) -> None:
    bg = "#0060ab" if ativo else "transparent"
    st.markdown(
        f'<div style="background:{bg}; border-radius:8px; margin-bottom:2px;">',
        unsafe_allow_html=True,
    )
    if st.button(label, key=f"nav_{key}", use_container_width=True):
        state.set_pagina(key)
    st.markdown("</div>", unsafe_allow_html=True)


def _respostas_atuais() -> None:
    if state.get_fase() != "entrevista" or not state.get_respostas():
        return
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:10px; font-weight:700; color:#666; '
        'text-transform:uppercase; letter-spacing:0.1em; '
        'margin-bottom:8px; padding-left:4px;">Respostas desta sessão</div>',
        unsafe_allow_html=True,
    )
    for i, r in enumerate(state.get_respostas()):
        st.markdown(
            f"""
            <div style="background:rgba(255,255,255,0.04); border-left:2px solid #469efe;
                        border-radius:4px; padding:8px 10px; margin-bottom:6px;">
              <div style="font-size:11px; font-weight:600; color:#ccc;">Q{i+1}. {r['titulo']}</div>
              <div style="font-size:10px; color:#81c784; margin-top:2px;">✓ Respondida</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _spacer() -> None:
    st.markdown("<br>" * 5, unsafe_allow_html=True)


def _btn_nova_sessao() -> None:
    if st.button("➕  Nova Sessão", use_container_width=True, key="btn_nova_sessao"):
        state.reset_para_selecao()


def _aviso_api_key_sidebar() -> None:
    if gemini_service.get_client():
        return
    st.markdown("<hr style='margin:16px 0; border-color:rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.warning("⚠️ Chave API não configurada.")
    user_key = st.text_input("Configurar Chave API Gemini:", type="password", key="sidebar_key")
    if user_key.strip():
        init_gemini(user_key.strip())
        st.rerun()


def _rodape() -> None:
    conta = state.get_user_conta() or "Usuário"
    st.markdown(
        f"""
        <div style="margin-top:16px; padding-top:16px;
                    border-top:1px solid rgba(255,255,255,0.06);
                    font-size:11px; color:#888;">
          Logado como <strong style="color:#ccc;">{conta}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🚪  Sair", use_container_width=True, key="btn_logout"):
        state.logout()
        st.rerun()
