"""
services/gemini_service.py
Toda a integração com a Google GenAI (Gemini).
Sem dependência de Streamlit — retorna valores puros (str / dict).
Quem chama exibe erros na UI se necessário.
"""
import json

import google.genai as genai
from google.genai import types

from config.settings import GEMINI_MODEL, DIFICULDADE_PADRAO, MODO_PADRAO
from models.schemas import AvaliacaoFinal
from utils.entrevista_helpers import montar_instrucao_avaliacao, montar_instrucao_entrevista


# ─── Cliente (singleton por processo) ────────────────────────

_client: genai.Client | None = None


def init_client(api_key: str) -> None:
    """Inicializa o cliente Gemini. Deve ser chamado uma vez no startup."""
    global _client
    _client = genai.Client(api_key=api_key)


def get_client() -> genai.Client | None:
    return _client


# ─── Funções de geração ───────────────────────────────────────

def primeira_pergunta(
    vaga: str,
    dificuldade: str = DIFICULDADE_PADRAO,
    modo: str = MODO_PADRAO,
) -> str | None:
    """Gera a primeira pergunta da entrevista."""
    if not _client:
        return None
    instrucao = montar_instrucao_entrevista(vaga, dificuldade, modo, n_respostas=0)
    resp = _client.models.generate_content(
        model=GEMINI_MODEL,
        contents="Olá, quero iniciar a entrevista.",
        config=types.GenerateContentConfig(system_instruction=instrucao),
    )
    return resp.text.strip()


def proxima_pergunta(
    historico: list[dict],
    vaga: str,
    dificuldade: str = DIFICULDADE_PADRAO,
    modo: str = MODO_PADRAO,
) -> str | None:
    """Gera a próxima pergunta com base no histórico."""
    if not _client:
        return None
    n_respostas = sum(1 for m in historico if m["role"] == "user")
    contents = _historico_para_contents(historico)
    instrucao = montar_instrucao_entrevista(vaga, dificuldade, modo, n_respostas)
    resp = _client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=instrucao),
    )
    return resp.text.strip()


def avaliar_entrevista(
    historico: list[dict],
    vaga: str,
    dificuldade: str = DIFICULDADE_PADRAO,
    modo: str = MODO_PADRAO,
) -> dict | None:
    """Gera a avaliação final estruturada via Pydantic schema."""
    if not _client:
        return None
    n = sum(1 for m in historico if m["role"] == "user")
    instrucao = montar_instrucao_avaliacao(vaga, dificuldade, modo, n)
    contents = _historico_para_contents(historico)
    resp = _client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AvaliacaoFinal,
            system_instruction=instrucao,
        ),
    )
    return json.loads(resp.text)


# ─── Helper interno ───────────────────────────────────────────

def _historico_para_contents(historico: list[dict]) -> list[dict]:
    """Converte o histórico de mensagens para o formato da API Gemini."""
    return [
        {
            "role": "user" if m["role"] == "user" else "model",
            "parts": [{"text": m["content"]}],
        }
        for m in historico
    ]
