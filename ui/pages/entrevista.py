"""
ui/pages/entrevista.py
Tela 3: loop da entrevista — exibe pergunta, aceita resposta, avança.
A lógica de fluxo (quantas perguntas, quando avaliar) fica aqui;
as chamadas à IA ficam em services/gemini_service.py.
"""
import streamlit as st

import core.state as state
from config.settings import get_info_pergunta
from core.persistence import arquivar_sessao_concluida, salvar_pendencia
from services import gemini_service
from ui.header import render_header

_PROX_FALLBACK  = "Conte-me mais sobre seus projetos anteriores nessa área."
_AVAL_FALLBACK  = {
    "resumo_geral": "O candidato demonstrou domínio sólido na área avaliada.",
    "comunicacao": 85, "tecnico": 90, "confianca": 80,
    "perguntas": [],
}
_AVAL_ENCERRADA = {
    "resumo_geral": (
        "A entrevista foi encerrada devido a respostas inadequadas, desconexas "
        "ou falta de seriedade durante o processo. As métricas refletem apenas "
        "o progresso realizado até a interrupção."
    ),
    "comunicacao": 0,
    "tecnico": 0,
    "confianca": 0,
    "perguntas": [],
}


def render() -> None:
    pendente = state.get_ia_pendente()
    if pendente:
        _tela_carregando_ia(pendente)
        return

    render_header("Simulador de Entrevista")

    erro = state.get_erro_ia()
    if erro:
        st.error(f"❌ {erro}")
        state.clear_erro_ia()

    n_resp = state.count_respostas()
    ultima = state.ultima_pergunta()

    _, col, _ = st.columns([1, 4, 1])
    with col:
        _cabecalho_pergunta(ultima, n_resp)
        resposta = _campo_resposta()
        _botoes_acao(resposta, n_resp)
        _dica_star()


# ─── Telas de carregamento ──────────────────────────────────────

def _tela_carregando_ia(pendente: dict) -> None:
    tipo = pendente.get("tipo", "proxima")
    if tipo == "concluir":
        titulo = "Gerando avaliação final..."
        subtitulo = "A IA está analisando suas respostas. Isso pode levar alguns segundos."
        emoji = "📊"
    else:
        titulo = "Gerando próxima pergunta..."
        subtitulo = "Aguarde enquanto a IA prepara a próxima questão."
        emoji = "🤖"

    render_header("Simulador de Entrevista")

    _, col, _ = st.columns([1, 4, 1])
    with col:
        st.markdown(
            f"""
            <div style="text-align:center; padding:56px 24px;">
              <div style="font-size:52px; margin-bottom:20px;">{emoji}</div>
              <h2 style="color:#191c1f; font-weight:700; margin-bottom:10px;">{titulo}</h2>
              <p style="color:#5b403e; font-size:15px; line-height:1.6;">{subtitulo}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.spinner(titulo):
        if tipo == "concluir":
            _executar_conclusao(pendente.get("encerrada_precoce", False))
        else:
            _executar_proxima(pendente)


# ─── Componentes ──────────────────────────────────────────────

def _cabecalho_pergunta(pergunta: str, n_resp: int) -> None:
    info = state.get_info_pergunta_atual()
    max_total = state.get_max_perguntas()
    cor_bloco = "#0060ab" if info["bloco"] == "tecnica" else "#7b1fa2"
    icone_bloco = "⚙️" if info["bloco"] == "tecnica" else "💬"

    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; align-items:center;
                    margin-bottom:24px;">
          <div style="background:#0060ab; width:60px; height:60px; border-radius:50%;
                      display:flex; align-items:center; justify-content:center;
                      color:#fff; font-size:26px;
                      box-shadow:0 4px 12px rgba(0,96,171,0.3); margin-bottom:12px;">🤖</div>
          <span style="background:{cor_bloco}; color:#fff; font-size:11px; font-weight:700;
                       padding:5px 12px; border-radius:999px; margin-bottom:10px;
                       text-transform:uppercase; letter-spacing:0.08em;">
            {icone_bloco} {info['bloco_label']} — {info['num_no_bloco']}/{info['total_bloco']}
          </span>
          <div style="font-size:11px; font-weight:700; color:#0060ab;
                      text-transform:uppercase; letter-spacing:0.12em;
                      margin-bottom:8px;">
            Pergunta {info['pergunta_atual']} de {max_total}
          </div>
          <h2 style="text-align:center; color:#191c1f; font-weight:700;
                     font-size:1.6rem; line-height:1.4;
                     padding:0 10px; max-width:700px;">
            "{pergunta}"
          </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _campo_resposta() -> str:
    return st.text_area(
        "Sua resposta",
        placeholder="Estruture sua resposta aqui... (dica: use o método STAR)",
        height=200,
        label_visibility="collapsed",
        key="input_resposta",
    )


def _botoes_acao(resposta: str, n_resp: int) -> None:
    col_pular, _, col_enviar = st.columns([1, 0.2, 2])
    with col_pular:
        if st.button("Pular ↷", use_container_width=True):
            _agendar_acao("(Questão pulada)", n_resp)
    with col_enviar:
        if st.button("Enviar Resposta & Avançar →", type="primary", use_container_width=True):
            if not resposta.strip():
                st.warning("Digite sua resposta antes de avançar.")
            else:
                _agendar_acao(resposta.strip(), n_resp)


def _dica_star() -> None:
    st.markdown(
        """
        <div style="margin-top:28px; background:#fff8f5; border-left:3px solid #b81120;
                    border-radius:4px; padding:14px 18px; max-width:500px;
                    margin-left:auto;">
          <div style="font-size:12px; font-weight:700; color:#b81120; margin-bottom:4px;">
            💡 Dica
          </div>
          <div style="font-size:12px; color:#5b403e; line-height:1.5;">
            Use o método <b>STAR</b> (Situação, Tarefa, Ação, Resultado)
            para dar mais clareza às suas respostas comportamentais.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─── Fluxo ────────────────────────────────────────────────────

def _agendar_acao(texto: str, n_resp: int) -> None:
    """Agenda chamada à IA e reroda — na próxima execução só aparece a tela de loading."""
    max_total = state.get_max_perguntas()
    info = state.get_info_pergunta_atual()
    titulo = f"Questão {n_resp + 1} ({info['bloco_label']})"

    if n_resp + 1 >= max_total:
        if state.count_respostas() < max_total:
            state.append_message("user", texto)
            state.append_resposta(titulo, texto)
            _persistir()
        state.set_ia_pendente({
            "tipo": "concluir",
            "encerrada_precoce": False,
            "n_resp": n_resp,
        })
    else:
        state.set_ia_pendente({
            "tipo": "proxima",
            "texto": texto,
            "n_resp": n_resp,
        })
    st.rerun()


def _executar_proxima(pendente: dict) -> None:
    state.clear_ia_pendente()
    texto = pendente["texto"]
    n_resp = pendente["n_resp"]
    temp_messages = state.get_messages() + [{"role": "user", "content": texto}]

    try:
        prox = gemini_service.proxima_pergunta(
            temp_messages,
            state.get_vaga(),
            state.get_dificuldade(),
            state.get_modo(),
        )
        err_msg = None
    except Exception as e:
        err_msg = f"Erro ao gerar pergunta: {e}"
        prox = None

    if err_msg:
        state.set_erro_ia(err_msg)
        st.rerun()
        return

    if not prox:
        if not gemini_service.get_client():
            state.set_erro_ia(
                "API Key não configurada! Configure sua chave API na barra lateral."
            )
        else:
            state.set_erro_ia("A IA retornou uma resposta vazia. Tente novamente.")
        st.rerun()
        return

    if "ENCERRAR_CHAT" in prox:
        info = state.get_info_pergunta_atual()
        titulo = f"Questão {n_resp + 1} ({info['bloco_label']})"
        state.append_message("user", texto)
        state.append_resposta(titulo, texto)
        _persistir()
        state.set_ia_pendente({
            "tipo": "concluir",
            "encerrada_precoce": True,
            "n_resp": n_resp,
        })
        st.rerun()
        return

    info = get_info_pergunta(state.get_modo(), n_resp + 1)
    titulo = f"Questão {n_resp + 1} ({info['bloco_label']})"
    state.append_message("user", texto)
    state.append_resposta(titulo, texto)
    state.append_message("assistant", prox)
    _persistir()
    st.rerun()


def _executar_conclusao(encerrada_precoce: bool = False) -> None:
    state.clear_ia_pendente()
    err_msg = None
    avaliacao = None

    try:
        avaliacao = gemini_service.avaliar_entrevista(
            state.get_messages(),
            state.get_vaga(),
            state.get_dificuldade(),
            state.get_modo(),
        )
    except Exception as e:
        err_msg = f"Erro ao gerar avaliação: {e}"

    if not avaliacao:
        avaliacao = _AVAL_ENCERRADA if encerrada_precoce else _AVAL_FALLBACK

    arquivar_sessao_concluida(
        user_id=state.get_user_id(),
        vaga=state.get_vaga(),
        historico_msgs=state.get_messages(),
        avaliacao=avaliacao,
        encerrada_precoce=encerrada_precoce,
        session_id=state.get_session_id(),
    )

    if err_msg:
        state.set_erro_ia(
            "Houve um erro ao gerar a avaliação com a IA. "
            "Um relatório básico foi salvo no seu histórico."
        )

    state.set_fase("relatorio")
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
