"""
ui/pages/dashboard.py
Página de dashboard: KPIs agregados, médias por competência,
evolução ao longo das sessões e tabela de notas por pergunta.
"""
import streamlit as st

import core.state as state
from core.cached_data import carregar_historico
from utils.helpers import media_avaliacao, svg_gauge


def render() -> None:
    from ui.header import render_header
    render_header("Dashboard de Desempenho")

    historico = carregar_historico(state.get_user_id())
    if not historico:
        _estado_vazio()
        return

    stats = _calcular_stats(historico)
    _kpis(historico, stats)
    st.markdown("<br>", unsafe_allow_html=True)
    _gauges_medias(stats)
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    _evolucao(historico, stats["medias"])
    st.markdown("<br><hr><br>", unsafe_allow_html=True)
    _notas_por_pergunta(historico)


# ─── Componentes ──────────────────────────────────────────────

def _estado_vazio() -> None:
    st.markdown(
        """
        <div style="text-align:center; padding:60px 20px; color:#888;">
          <div style="font-size:48px; margin-bottom:16px;">📊</div>
          <h3 style="color:#5b403e;">Sem dados ainda</h3>
          <p>Complete ao menos uma entrevista para ver seu dashboard.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _calcular_stats(historico: list) -> dict:
    avaliacoes = [s.get("avaliacao", {}) for s in historico]
    medias = [media_avaliacao(a) for a in avaliacoes]
    return {
        "medias":     medias,
        "media_com":  round(sum(a.get("comunicacao", 0) for a in avaliacoes) / len(avaliacoes)),
        "media_tec":  round(sum(a.get("tecnico", 0)     for a in avaliacoes) / len(avaliacoes)),
        "media_conf": round(sum(a.get("confianca", 0)   for a in avaliacoes) / len(avaliacoes)),
        "media_geral":round(sum(medias) / len(medias)),
        "vagas":      len(set(s.get("vaga", "") for s in historico)),
    }


def _kpis(historico: list, stats: dict) -> None:
    k1, k2, k3, k4 = st.columns(4)
    for col, label, val, icon in [
        (k1, "Sessões Realizadas", len(historico),           "🎯"),
        (k2, "Vagas Testadas",     stats["vagas"],           "💼"),
        (k3, "Média Geral",        f"{stats['media_geral']}%","⭐"),
        (k4, "Melhor Sessão",      f"{max(stats['medias'])}%","🏆"),
    ]:
        col.markdown(
            f"""
            <div class="card" style="text-align:center; padding:20px;">
              <div style="font-size:28px; margin-bottom:6px;">{icon}</div>
              <div style="font-size:26px; font-weight:700; color:#191c1f;">{val}</div>
              <div style="font-size:12px; color:#888; margin-top:4px;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _gauges_medias(stats: dict) -> None:
    st.markdown(
        "<h3 style='color:#191c1f; font-weight:700; margin-bottom:16px;'>"
        "Médias por Competência</h3>",
        unsafe_allow_html=True,
    )
    g1, g2, g3 = st.columns(3)
    for col, label, val, desc in [
        (g1, "Comunicação",        stats["media_com"],  "Média entre todas as sessões."),
        (g2, "Habilidade Técnica", stats["media_tec"],  "Profundidade de conhecimento."),
        (g3, "Confiança",          stats["media_conf"], "Postura e segurança geral."),
    ]:
        with col:
            col.markdown(svg_gauge(val, label, desc), unsafe_allow_html=True)


def _evolucao(historico: list, medias: list) -> None:
    st.markdown(
        "<h3 style='color:#191c1f; font-weight:700; margin-bottom:16px;'>"
        "Evolução das Sessões</h3>",
        unsafe_allow_html=True,
    )
    for sessao, media in zip(historico, medias):
        cor = "#0060ab" if media >= 70 else "#b81120"
        st.markdown(
            f"""
            <div style="margin-bottom:12px;">
              <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="font-size:13px; font-weight:600; color:#191c1f;">
                  {sessao.get('vaga','')}
                  <span style="font-weight:400; color:#888; font-size:12px;">
                    — {sessao.get('data','')}
                  </span>
                </span>
                <span style="font-size:13px; font-weight:700; color:{cor};">{media}%</span>
              </div>
              <div style="background:#eceef2; border-radius:999px; height:8px; overflow:hidden;">
                <div style="background:{cor}; height:8px; border-radius:999px; width:{media}%;"></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _notas_por_pergunta(historico: list) -> None:
    st.markdown(
        "<h3 style='color:#191c1f; font-weight:700; margin-bottom:16px;'>"
        "Últimas Sessões — Notas por Pergunta</h3>",
        unsafe_allow_html=True,
    )
    for sessao in reversed(historico[-3:]):
        pergs = sessao.get("avaliacao", {}).get("perguntas", [])
        if not pergs:
            continue
        st.markdown(
            f"<div style='font-size:13px; font-weight:700; color:#0060ab;"
            f" margin-bottom:8px;'>📌 {sessao.get('vaga','')} — {sessao.get('data','')}</div>",
            unsafe_allow_html=True,
        )
        cols = st.columns(len(pergs))
        for j, (col, p) in enumerate(zip(cols, pergs)):
            nota = p.get("nota", 0)
            cor  = "#0060ab" if nota >= 70 else "#b81120"
            col.markdown(
                f"""
                <div style="text-align:center; background:#fff; border:1px solid #e0e2e6;
                            border-radius:8px; padding:12px 6px;">
                  <div style="font-size:20px; font-weight:700; color:{cor};">{nota}</div>
                  <div style="font-size:10px; color:#888; margin-top:2px;">Q{j+1}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("<br>", unsafe_allow_html=True)
