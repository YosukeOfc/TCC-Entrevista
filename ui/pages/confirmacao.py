"""
ui/pages/confirmacao.py
Tela 2: confirmação da vaga antes de iniciar as perguntas.
"""
import streamlit as st

import core.state as state
from config.settings import OPCOES_DIFICULDADE, OPCOES_MODO
from core.persistence import salvar_pendencia
from services import gemini_service
from ui.header import render_header

_PERGUNTA_FALLBACK = (
    "Olá! Vamos começar a entrevista. "
    "Fale um pouco sobre você e sua experiência com essa vaga."
)


def render() -> None:
    render_header("Simulador de Entrevista")

    total = state.get_max_perguntas()
    modo_label = OPCOES_MODO.get(state.get_modo(), state.get_modo())
    diff_label = OPCOES_DIFICULDADE.get(state.get_dificuldade(), state.get_dificuldade())

    desc_perguntas = (
        f"Serão feitas <b>{total} perguntas</b> ({modo_label.lower()})."
        if state.get_modo() != "ambas"
        else (
            f"Serão <b>10 perguntas técnicas</b> seguidas de "
            f"<b>10 perguntas socioemocionais</b> (20 no total)."
        )
    )

    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="card" style="text-align:center;">
              <div style="font-size:40px; margin-bottom:12px;">🎯</div>
              <h3 style="color:#191c1f; margin-bottom:4px;">Vaga selecionada:</h3>
              <h2 style="color:#0060ab; margin:8px 0 12px;">{state.get_vaga()}</h2>
              <p style="color:#5b403e; font-size:13px; margin-bottom:6px;">
                <b>Dificuldade:</b> {diff_label}
              </p>
              <p style="color:#5b403e; font-size:13px; margin-bottom:12px;">
                <b>Modo:</b> {modo_label}
              </p>
              <p style="color:#5b403e; font-size:14px;">
                {desc_perguntas} Pronto?
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Confirmar e Iniciar", use_container_width=True, type="primary"):
                _confirmar()
        with c2:
            if st.button("↩️ Mudar Vaga", use_container_width=True):
                state.reset_para_selecao()
                st.rerun()


def _confirmar() -> None:
    with st.spinner("Preparando a entrevista..."):
        try:
            primeira = gemini_service.primeira_pergunta(
                state.get_vaga(),
                state.get_dificuldade(),
                state.get_modo(),
            )
        except Exception as e:
            st.error(f"Erro ao gerar pergunta: {e}")
            primeira = None

    state.iniciar_entrevista(
        vaga=state.get_vaga(),
        primeira_pergunta=primeira or _PERGUNTA_FALLBACK,
    )
    _persistir()
    st.rerun()


def _persistir() -> None:
    salvar_pendencia(
        user_id=state.get_user_id(),
        session_id=state.get_session_id(),
        vaga=state.get_vaga(),
        fase=state.get_fase(),
        historico=state.get_messages(),
        respostas_anteriores=state.get_respostas(),
        data_inicio=state.get_data_inicio(),
        dificuldade=state.get_dificuldade(),
        modo_perguntas=state.get_modo(),
    )
