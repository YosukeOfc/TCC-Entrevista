"""
ui/pages/selecao.py
Tela 1: seleção da vaga antes de iniciar a entrevista.
"""
import streamlit as st

import core.state as state
from config.settings import CARGOS_RAPIDOS, DIFICULDADE_PADRAO, MODO_PADRAO, OPCOES_DIFICULDADE, OPCOES_MODO
from services import gemini_service
from ui.header import render_header


def render() -> None:
    render_header("Simulador de Entrevista")

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <h1 style="text-align:center; font-size:2.2rem; font-weight:700;
                       color:#191c1f; margin-bottom:10px;">
              Para qual cargo você está se preparando?
            </h1>
            <p style="text-align:center; color:#5b403e; font-size:1rem;
                      margin-bottom:28px; line-height:1.6;">
              Selecione sua profissão ou digite a sua. Nossa IA personalizará
              toda a experiência de entrevista.
            </p>
            """,
            unsafe_allow_html=True,
        )

        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(
                "<div style='font-weight:600; font-size:14px; margin-bottom:10px;"
                " color:#191c1f;'>Profissão Alvo</div>",
                unsafe_allow_html=True,
            )

            escolha = st.selectbox(
                "Cargo",
                label_visibility="collapsed",
                options=["Selecione ou use campo abaixo..."] + CARGOS_RAPIDOS,
            )
            texto_livre = st.text_input(
                "Ou digite o cargo aqui:",
                placeholder="Ex: Desenvolvedor Flutter Pleno",
            )

            vaga_final = _resolver_vaga(escolha, texto_livre)
            _aviso_api_key()

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<div style='font-weight:600; font-size:14px; margin-bottom:8px; color:#191c1f;'>"
                "Nível de dificuldade</div>",
                unsafe_allow_html=True,
            )
            dificuldade = st.selectbox(
                "Dificuldade",
                label_visibility="collapsed",
                options=list(OPCOES_DIFICULDADE.keys()),
                format_func=lambda k: OPCOES_DIFICULDADE[k],
                index=list(OPCOES_DIFICULDADE.keys()).index(DIFICULDADE_PADRAO),
                key="sel_dificuldade",
            )

            st.markdown(
                "<div style='font-weight:600; font-size:14px; margin:16px 0 8px; color:#191c1f;'>"
                "Modo de perguntas</div>",
                unsafe_allow_html=True,
            )
            modo = st.selectbox(
                "Modo",
                label_visibility="collapsed",
                options=list(OPCOES_MODO.keys()),
                format_func=lambda k: OPCOES_MODO[k],
                index=list(OPCOES_MODO.keys()).index(MODO_PADRAO),
                key="sel_modo",
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Começar Sua Sessão →", use_container_width=True, type="primary"):
                _iniciar(vaga_final, dificuldade, modo)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            "<p style='text-align:center; font-size:12px; color:#bbb; margin-top:30px;'>"
            "© 2026 InterviewAI. Preparação de nível profissional.</p>",
            unsafe_allow_html=True,
        )


# ─── Helpers ─────────────────────────────────────────────────

def _resolver_vaga(escolha: str, texto_livre: str) -> str:
    if texto_livre.strip():
        return texto_livre.strip()
    if escolha != "Selecione ou use campo abaixo...":
        return escolha
    return ""


def _aviso_api_key() -> None:
    if gemini_service.get_client():
        return
    st.warning(
        "⚠️ Chave API não configurada. "
        "Defina GEMINI_API_KEY nos secrets do Streamlit ou como variável de ambiente."
    )
    user_key = st.text_input("Cole sua chave Gemini aqui:", type="password", key="inline_key")
    if user_key:
        gemini_service.init_client(user_key)


def _iniciar(vaga: str, dificuldade: str, modo: str) -> None:
    if not vaga:
        st.warning("Selecione ou digite uma profissão.")
        return
    state.criar_nova_sessao(vaga, dificuldade, modo)
    st.rerun()
