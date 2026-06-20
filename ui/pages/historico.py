"""
ui/pages/historico.py
Página de histórico: lista todas as sessões concluídas com detalhes expansíveis.
"""
import streamlit as st

import core.state as state
from core.cached_data import carregar_historico
from utils.helpers import cor_nota, estrelas


def render() -> None:
    from ui.header import render_header
    render_header("Histórico de Sessões")

    historico = carregar_historico(state.get_user_id())

    if not historico:
        _estado_vazio()
        return

    st.markdown(
        f"<p style='color:#888; font-size:13px; margin-bottom:24px;'>"
        f"{len(historico)} sessão(ões) concluída(s)</p>",
        unsafe_allow_html=True,
    )

    for idx, sessao in enumerate(reversed(historico)):
        _card_sessao(sessao, aberto=(idx == 0), idx=idx)


# ─── Componentes ──────────────────────────────────────────────

def _estado_vazio() -> None:
    st.markdown(
        """
        <div style="text-align:center; padding:60px 20px; color:#888;">
          <div style="font-size:48px; margin-bottom:16px;">📋</div>
          <h3 style="color:#5b403e;">Nenhuma sessão concluída ainda</h3>
          <p>Complete uma entrevista para ver o histórico aqui.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.fragment
def _card_sessao(sessao: dict, aberto: bool, idx: int) -> None:
    aval  = sessao.get("avaliacao", {})
    media = round((
        aval.get("comunicacao", 0) +
        aval.get("tecnico", 0) +
        aval.get("confianca", 0)
    ) / 3)

    vaga = sessao.get("vaga", "").strip() or "Cargo não especificado"
    titulo = (
        f"📅 {sessao.get('data', '')}  —  "
        f"**{vaga}**  —  Média: {media}/100"
    )

    with st.expander(titulo, expanded=aberto, key=f"hist_exp_{idx}"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Comunicação", f"{aval.get('comunicacao', 0)}%")
        c2.metric("Técnico",     f"{aval.get('tecnico', 0)}%")
        c3.metric("Confiança",   f"{aval.get('confianca', 0)}%")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="background:#e3f2fd; border-left:4px solid #0060ab;
                        border-radius:6px; padding:14px 18px; font-size:13px;
                        color:#003461; line-height:1.6; margin-bottom:16px;">
              {aval.get('resumo_geral', '')}
            </div>
            """,
            unsafe_allow_html=True,
        )

        for i, p in enumerate(aval.get("perguntas", [])):
            nota = p.get("nota", 0)
            st.markdown(
                f"""
                <div style="border:1px solid #e0e2e6; border-radius:8px;
                            padding:16px; margin-bottom:10px;">
                  <div style="display:flex; justify-content:space-between;
                              margin-bottom:8px;">
                    <span style="font-size:11px; font-weight:700; color:#0060ab;">
                      PERGUNTA {i+1}
                    </span>
                    <span style="font-weight:700; color:{cor_nota(nota)};">
                      {nota}/100 &nbsp;{estrelas(nota)}
                    </span>
                  </div>
                  <div style="font-weight:600; color:#191c1f; font-size:13px;
                              margin-bottom:6px;">{p.get('pergunta', '')}</div>
                  <div style="font-size:12px; color:#5b403e; line-height:1.6;">
                    {p.get('feedback', '')}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
