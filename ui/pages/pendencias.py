"""
ui/pages/pendencias.py
Página de pendências: lista todas as sessões não concluídas com a opção de retomar ou excluir.
"""
from datetime import datetime
import streamlit as st

import core.state as state
from config.settings import MODO_PADRAO, get_total_perguntas
from core.cached_data import carregar_pendencias
from core.persistence import remover_pendencia


def render() -> None:
    from ui.header import render_header
    render_header("Entrevistas Pendentes")

    pendencias = carregar_pendencias(state.get_user_id())

    if not pendencias:
        _estado_vazio()
        return

    st.markdown(
        f"<p style='color:#888; font-size:13px; margin-bottom:24px;'>"
        f"Você possui {len(pendencias)} entrevista(s) pendente(s)</p>",
        unsafe_allow_html=True,
    )

    # Ordena as pendências por data (mais recente primeiro)
    for session_id in sorted(pendencias.keys(), reverse=True):
        _card_pendencia(session_id, pendencias[session_id])


# ─── Componentes ──────────────────────────────────────────────

def _estado_vazio() -> None:
    st.markdown(
        """
        <div style="text-align:center; padding:60px 20px; color:#888;">
          <div style="font-size:48px; margin-bottom:16px;">⏳</div>
          <h3 style="color:#5b403e;">Nenhuma entrevista pendente</h3>
          <p>As entrevistas que você não terminar de responder aparecerão aqui para você retomar quando quiser.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _card_pendencia(session_id: str, sessao: dict) -> None:
    vaga = sessao.get("vaga", "").strip() or "Cargo não especificado"
    data_inicio = sessao.get("data_inicio", "")
    
    # Formatação amigável da data
    try:
        dt = datetime.fromisoformat(data_inicio)
        data_str = dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        data_str = data_inicio

    respostas = sessao.get("respostas_anteriores", [])
    n_respostas = len(respostas)
    max_total = get_total_perguntas(sessao.get("modo_perguntas", MODO_PADRAO))
    progresso_str = f"Respondidas: {n_respostas} de {max_total} perguntas"

    with st.container():
        # Renderização do Card com Estilo Premium
        st.markdown(
            f"""
            <div class="card" style="margin-bottom:16px; border-left:4px solid #f57c00; padding:18px;">
              <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                  <span style="background:#fff3e0; color:#e65100; font-size:10px; font-weight:700;
                               padding:4px 8px; border-radius:4px; text-transform:uppercase;">
                    EM ANDAMENTO
                  </span>
                  <h3 style="margin:8px 0 4px 0; font-size:1.3rem; font-weight:700; color:#191c1f;">
                    {vaga}
                  </h3>
                  <div style="font-size:12px; color:#888; margin-bottom:8px;">
                    Iniciada em: {data_str}
                  </div>
                  <div style="font-size:13px; color:#5b403e; font-weight:600;">
                    📊 {progresso_str}
                  </div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Botões de ação alinhados
        col_retomar, col_excluir, _ = st.columns([1.2, 1, 3])
        with col_retomar:
            if st.button("🎤 Retomar Entrevista", key=f"retomar_{session_id}", type="primary", use_container_width=True):
                state.carregar_sessao_ativa(sessao)
                st.rerun()
        with col_excluir:
            if st.button("🗑️ Excluir", key=f"excluir_{session_id}", use_container_width=True):
                remover_pendencia(state.get_user_id(), session_id)
                st.rerun()
        
        st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)
