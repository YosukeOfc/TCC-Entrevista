"""
core/persistence.py
Toda a lógica de leitura e escrita em data.json.
Estrutura do JSON:
  {
    "usuarios": {
      "email@exemplo.com": {
        "conta": "...",
        "email": "...",
        "senha_hash": "...",
        "historico": [ { vaga, data, avaliacao, historico }, ... ],
        "pendencias": { session_id: { ... } }
      }
    }
  }
Sem dependência de Streamlit.
"""
import json
import os
from datetime import datetime

from config.settings import DATA_PATH


# ─── Cache em memória (evita múltiplas leituras por requisição) ─

_mem_cache: dict | None = None
_mem_mtime: float = -1.0


def get_file_mtime() -> float:
    """Timestamp do data.json — usado para invalidar cache entre reruns."""
    try:
        return os.path.getmtime(DATA_PATH)
    except OSError:
        return 0.0


def _invalidar_mem_cache() -> None:
    global _mem_cache, _mem_mtime
    _mem_cache = None
    _mem_mtime = -1.0


# ─── Primitivos ───────────────────────────────────────────────

def _ler() -> dict:
    """Lê o arquivo data.json e retorna o dicionário (com cache em memória)."""
    global _mem_cache, _mem_mtime
    mtime = get_file_mtime()
    if _mem_cache is not None and mtime == _mem_mtime:
        return _mem_cache

    dados: dict = {}
    try:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                dados = json.load(f)
    except Exception:
        pass

    _mem_cache = dados
    _mem_mtime = mtime
    return dados


def _gravar(dados: dict) -> None:
    """Grava o dicionário no data.json."""
    global _mem_cache, _mem_mtime
    os.makedirs(os.path.dirname(DATA_PATH) or ".", exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    _mem_cache = dados
    _mem_mtime = get_file_mtime()


def _dados_usuario(user_id: str) -> dict | None:
    if not user_id:
        return None
    return _ler().get("usuarios", {}).get(user_id)


def _garantir_usuario(user_id: str, dados: dict | None = None) -> tuple[dict, dict]:
    if dados is None:
        dados = _ler()
    usuarios = dados.setdefault("usuarios", {})
    if user_id not in usuarios:
        raise ValueError("Usuário não encontrado.")
    return dados, usuarios[user_id]


# ─── Pendências ───────────────────────────────────────────────

def carregar_pendencias(user_id: str) -> dict:
    """Retorna o dicionário de pendências do usuário."""
    usuario = _dados_usuario(user_id)
    if not usuario:
        return {}
    return usuario.get("pendencias", {})


def salvar_pendencia(
    user_id: str,
    session_id: str,
    vaga: str,
    fase: str,
    historico: list,
    respostas_anteriores: list,
    data_inicio: str,
    dificuldade: str = "medio",
    modo_perguntas: str = "tecnicas",
) -> None:
    """Persiste ou atualiza uma pendência do usuário."""
    if not user_id or not session_id:
        return
    dados = _ler()
    usuario = dados.setdefault("usuarios", {}).setdefault(user_id, {
        "historico": [],
        "pendencias": {},
    })
    if "pendencias" not in usuario:
        usuario["pendencias"] = {}
    usuario["pendencias"][session_id] = {
        "session_id": session_id,
        "vaga": vaga,
        "fase": fase,
        "historico": historico,
        "respostas_anteriores": respostas_anteriores,
        "data_inicio": data_inicio,
        "dificuldade": dificuldade,
        "modo_perguntas": modo_perguntas,
    }
    _gravar(dados)


def remover_pendencia(user_id: str, session_id: str) -> None:
    """Remove uma pendência específica do usuário."""
    if not user_id or not session_id:
        return
    dados = _ler()
    usuario = dados.get("usuarios", {}).get(user_id)
    if not usuario:
        return
    pendencias = usuario.get("pendencias", {})
    if session_id in pendencias:
        del pendencias[session_id]
        _gravar(dados)


# ─── Histórico de sessões concluídas ─────────────────────────

def carregar_historico(user_id: str) -> list:
    """Retorna a lista de sessões concluídas do usuário."""
    usuario = _dados_usuario(user_id)
    if not usuario:
        return []
    return usuario.get("historico", [])


def arquivar_sessao_concluida(
    user_id: str,
    vaga: str,
    historico_msgs: list,
    avaliacao: dict,
    encerrada_precoce: bool = False,
    session_id: str = "",
) -> None:
    """Move a sessão atual para o histórico do usuário e limpa a pendência."""
    if not user_id:
        return
    dados, usuario = _garantir_usuario(user_id)
    historico_list = usuario.setdefault("historico", [])
    historico_list.append({
        "vaga": vaga,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "avaliacao": avaliacao,
        "historico": historico_msgs,
        "encerrada_precoce": encerrada_precoce,
    })

    pendencias = usuario.get("pendencias", {})
    if session_id and session_id in pendencias:
        del pendencias[session_id]

    _gravar(dados)
