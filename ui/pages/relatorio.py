"""
ui/pages/relatorio.py
Tela 4: relatório final da sessão mais recente concluída.
"""
import streamlit as st

import core.state as state
from config.settings import SECOES_RELATORIO
from core.cached_data import carregar_historico
from utils.helpers import cor_nota, estrelas, svg_gauge


def render() -> None:
    historico = carregar_historico(state.get_user_id())
    if not historico:
        st.error("Nenhuma avaliação encontrada. Inicie uma nova sessão.")
        return

    dados = historico[-1]
    aval  = dados.get("avaliacao", {})
    vaga  = dados.get("vaga", "").strip() or "Cargo não especificado"
    pergs = aval.get("perguntas", [])
    encerrada_precoce = dados.get("encerrada_precoce", False)

    _cabecalho(vaga, dados.get("data", ""), aval, pergs)

    if encerrada_precoce:
        st.markdown(
            """
            <div style="background-color: #ffebee; border-left: 4px solid #d32f2f; padding: 16px; border-radius: 8px; margin-bottom: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <h4 style="color: #c62828; margin: 0 0 6px 0; font-weight: 700; font-size: 15px; display: flex; align-items: center; gap: 8px;">
                    ⚠️ Entrevista Encerrada Precocemente pela IA
                </h4>
                <p style="color: #b71c1c; margin: 0; font-size: 13px; line-height: 1.5;">
                    A inteligência artificial detectou que as respostas fornecidas não condiziam com uma entrevista séria (ou continham conteúdos desconexos/inadequados) e encerrou a sessão imediatamente. As métricas e notas abaixo refletem apenas o progresso realizado até a interrupção.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    _resumo_geral(aval)
    _gauges(aval)
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    _avaliacao_detalhada(pergs)
    _rodape()


# ─── Componentes ──────────────────────────────────────────────

def _cabecalho(vaga: str, data: str, aval: dict, pergs: list) -> None:
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
              <span style="background:#0060ab; color:#fff; font-size:10px; font-weight:700;
                           padding:4px 10px; border-radius:4px;
                           text-transform:uppercase;">{vaga}</span>
              <span style="font-size:12px; color:#888;">• {data}</span>
            </div>
            <h1 style="margin:0; font-size:2rem; font-weight:700; color:#191c1f;">
              Resumo de Desempenho
            </h1>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        txt = _gerar_txt(vaga, data, aval, pergs)
        st.download_button(
            "📥 Exportar TXT", txt, "relatorio.txt", "text/plain",
            use_container_width=True,
        )
    st.markdown("<hr style='margin:16px 0;'>", unsafe_allow_html=True)


def _resumo_geral(aval: dict) -> None:
    st.markdown(
        f"""
        <div style="background:#e3f2fd; border-left:4px solid #0060ab;
                    border-radius:8px; padding:18px 22px; margin-bottom:28px;
                    font-size:14px; color:#003461; line-height:1.65;">
          {aval.get('resumo_geral', '')}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _gauges(aval: dict) -> None:
    g1, g2, g3 = st.columns(3)
    for col, chave, label, desc in [
        (g1, "comunicacao",  "Comunicação",        "Clareza e articulação das respostas."),
        (g2, "tecnico",      "Habilidade Técnica",  "Profundidade do conhecimento."),
        (g3, "confianca",    "Confiança",           "Postura e profissionalismo."),
    ]:
        with col:
            col.markdown(
                svg_gauge(aval.get(chave, 0), label, desc),
                unsafe_allow_html=True,
            )


def _avaliacao_detalhada(pergs: list) -> None:
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between;
                    align-items:baseline; margin-bottom:20px;">
          <h2 style="margin:0; font-size:1.5rem; font-weight:700; color:#191c1f;">
            Avaliação Detalhada
          </h2>
          <span style="color:#888; font-size:13px;">{len(pergs)} perguntas avaliadas</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for i, p in enumerate(pergs):
        nota   = p.get("nota", 0)
        secao  = SECOES_RELATORIO[i] if i < len(SECOES_RELATORIO) else f"PERGUNTA {i+1}"
        st.markdown(
            f"""
            <div class="card">
              <div style="display:flex; justify-content:space-between;
                          align-items:flex-start; margin-bottom:10px;">
                <span style="font-size:10px; font-weight:700; color:#0060ab;
                             text-transform:uppercase; letter-spacing:0.08em;">
                  {str(i+1).zfill(2)} • {secao}
                </span>
                <div style="text-align:right;">
                  <div style="font-size:18px; font-weight:700; color:{cor_nota(nota)};">
                    {nota}/100
                  </div>
                  <div style="color:#ffb300; font-size:13px;">{estrelas(nota)}</div>
                </div>
              </div>
              <h3 style="margin:0 0 10px; font-size:1.05rem; font-weight:700;
                         color:#191c1f; line-height:1.4;">
                "{p.get('pergunta', '')}"
              </h3>
              <p style="font-size:13px; color:#5b403e; line-height:1.65; margin:0;">
                {p.get('feedback', '')}
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _rodape() -> None:
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    _, bc, _ = st.columns([1, 1, 1])
    with bc:
        if st.button("🔄 Iniciar Nova Sessão", type="primary", use_container_width=True):
            state.reset_para_selecao()
            st.rerun()


def _gerar_txt(vaga: str, data: str, aval: dict, pergs: list) -> str:
    txt  = f"RELATÓRIO InterviewAI\nVaga: {vaga}\nData: {data}\n\n"
    txt += f"Resumo Geral:\n{aval.get('resumo_geral', '')}\n\n"
    txt += f"Comunicação: {aval.get('comunicacao', 0)}%\n"
    txt += f"Técnico:     {aval.get('tecnico', 0)}%\n"
    txt += f"Confiança:   {aval.get('confianca', 0)}%\n\n"
    for i, p in enumerate(pergs, 1):
        txt += f"Pergunta {i}: {p.get('pergunta', '')}\n"
        txt += f"Nota: {p.get('nota', 0)}/100\n"
        txt += f"Feedback: {p.get('feedback', '')}\n\n"
    return txt
