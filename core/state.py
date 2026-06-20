"""
core/state.py
Centraliza toda a inicialização e acesso ao st.session_state.
Provê getters/setters com nomes claros para evitar "magic strings"
espalhadas pelo código.
"""
from datetime import datetime
import streamlit as st

from config.settings import DIFICULDADE_PADRAO, MODO_PADRAO, get_info_pergunta, get_total_perguntas


# ─── Inicialização ────────────────────────────────────────────

def init_state() -> None:
    """
    Inicializa o session_state na primeira execução.
    Sempre inicializa no estado limpo (selecao) ao abrir/dar F5.
    Para continuar uma pendente, o usuário deve ir ao menu 'Pendências'.
    """
    if "auth_user_id" not in st.session_state:
        st.session_state.auth_user_id = ""
        st.session_state.auth_conta = ""
        st.session_state.auth_email = ""

    if "fase" not in st.session_state:
        _reset_entrevista()

    if "pagina" not in st.session_state:
        st.session_state.pagina = "entrevista"

    if "ia_pendente" not in st.session_state:
        st.session_state.ia_pendente = None

    if "erro_ia" not in st.session_state:
        st.session_state.erro_ia = ""


# ─── Getters ─────────────────────────────────────────────────

def get_session_id() -> str: return st.session_state.get("session_id", "")
def get_fase()    -> str:   return st.session_state.get("fase", "selecao")
def get_vaga()    -> str:   return st.session_state.get("vaga", "")
def get_messages() -> list: return st.session_state.get("messages", [])
def get_respostas() -> list:return st.session_state.get("respostas_anteriores", [])
def get_pagina()  -> str:   return st.session_state.get("pagina", "entrevista")
def get_data_inicio() -> str: return st.session_state.get("data_inicio", _now())
def get_user_id() -> str: return st.session_state.get("auth_user_id", "")
def get_user_conta() -> str: return st.session_state.get("auth_conta", "")
def get_user_email() -> str: return st.session_state.get("auth_email", "")
def is_authenticated() -> bool: return bool(get_user_id())
def get_ia_pendente() -> dict | None: return st.session_state.get("ia_pendente")
def is_ia_carregando() -> bool: return bool(get_ia_pendente())
def get_erro_ia() -> str: return st.session_state.get("erro_ia", "")
def get_dificuldade() -> str: return st.session_state.get("dificuldade", DIFICULDADE_PADRAO)
def get_modo() -> str: return st.session_state.get("modo_perguntas", MODO_PADRAO)
def get_max_perguntas() -> int: return get_total_perguntas(get_modo())
def get_info_pergunta_atual() -> dict: return get_info_pergunta(get_modo(), count_respostas())

def count_respostas() -> int:
    return len([m for m in get_messages() if m["role"] == "user"])

def ultima_pergunta() -> str:
    msgs = get_messages()
    return next(
        (m["content"] for m in reversed(msgs) if m["role"] == "assistant"),
        "Como você se descreve profissionalmente?"
    )


# ─── Setters / Mutações ──────────────────────────────────────

def set_session_id(val: str) -> None: st.session_state.session_id = val
def set_fase(fase: str)   -> None: st.session_state.fase   = fase
def set_vaga(vaga: str)   -> None: st.session_state.vaga   = vaga
def set_pagina(p: str)    -> None: st.session_state.pagina = p

def set_ia_pendente(payload: dict) -> None:
    st.session_state.ia_pendente = payload

def clear_ia_pendente() -> None:
    st.session_state.ia_pendente = None

def set_erro_ia(msg: str) -> None:
    st.session_state.erro_ia = msg

def clear_erro_ia() -> None:
    st.session_state.erro_ia = ""

def set_messages(msgs: list) -> None:
    st.session_state.messages = msgs

def append_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})

def append_resposta(titulo: str, resposta: str) -> None:
    st.session_state.respostas_anteriores.append({
        "titulo": titulo,
        "resposta": resposta,
    })

def iniciar_entrevista(vaga: str, primeira_pergunta: str) -> None:
    st.session_state.fase               = "entrevista"
    st.session_state.vaga               = vaga
    st.session_state.messages           = [{"role": "assistant", "content": primeira_pergunta}]
    st.session_state.respostas_anteriores = []
    # Mantém o session_id gerado anteriormente na criação, ou cria um novo se não existir
    if not st.session_state.get("session_id"):
        st.session_state.data_inicio    = _now()
        st.session_state.session_id     = st.session_state.data_inicio
    else:
        st.session_state.data_inicio    = st.session_state.session_id

def criar_nova_sessao(vaga: str, dificuldade: str, modo_perguntas: str) -> None:
    """Cria uma nova sessão na fase de confirmação."""
    st.session_state.session_id         = _now()
    st.session_state.fase               = "confirmacao"
    st.session_state.vaga               = vaga
    st.session_state.dificuldade        = dificuldade
    st.session_state.modo_perguntas     = modo_perguntas
    st.session_state.messages           = []
    st.session_state.respostas_anteriores = []
    st.session_state.data_inicio        = st.session_state.session_id

def carregar_sessao_ativa(sessao: dict) -> None:
    """Carrega os dados de uma sessão pendente para o session_state ativo."""
    st.session_state.session_id         = sessao.get("session_id", sessao.get("data_inicio", ""))
    st.session_state.fase               = sessao.get("fase", "entrevista")
    st.session_state.vaga               = sessao.get("vaga", "")
    st.session_state.dificuldade        = sessao.get("dificuldade", DIFICULDADE_PADRAO)
    st.session_state.modo_perguntas       = sessao.get("modo_perguntas", MODO_PADRAO)
    st.session_state.messages           = sessao.get("historico", [])
    st.session_state.respostas_anteriores = sessao.get("respostas_anteriores", [])
    st.session_state.data_inicio        = sessao.get("data_inicio", _now())
    st.session_state.pagina             = "entrevista"

def reset_para_selecao() -> None:
    """Volta ao início sem apagar o histórico de sessões concluídas."""
    _reset_entrevista()
    st.session_state.pagina = "entrevista"


def login(usuario: dict) -> None:
    st.session_state.auth_user_id = usuario["user_id"]
    st.session_state.auth_conta = usuario["conta"]
    st.session_state.auth_email = usuario["email"]
    _reset_entrevista()
    st.session_state.pagina = "entrevista"


def logout() -> None:
    st.session_state.auth_user_id = ""
    st.session_state.auth_conta = ""
    st.session_state.auth_email = ""
    _reset_entrevista()
    st.session_state.pagina = "entrevista"


# ─── Helpers internos ─────────────────────────────────────────

def _now() -> str:
    return datetime.now().isoformat()

def _reset_entrevista() -> None:
    st.session_state.session_id         = ""
    st.session_state.fase               = "selecao"
    st.session_state.vaga               = ""
    st.session_state.dificuldade        = DIFICULDADE_PADRAO
    st.session_state.modo_perguntas       = MODO_PADRAO
    st.session_state.messages           = []
    st.session_state.respostas_anteriores = []
    st.session_state.data_inicio        = _now()
    st.session_state.ia_pendente        = None
    st.session_state.erro_ia            = ""
