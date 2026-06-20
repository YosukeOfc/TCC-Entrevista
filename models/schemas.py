"""
models/schemas.py
Definição dos schemas Pydantic usados para validar respostas da IA.
Sem dependência de Streamlit ou lógica de negócio.
"""
from pydantic import BaseModel, Field


class AvaliacaoPergunta(BaseModel):
    pergunta: str
    resposta_resumida: str
    nota: int = Field(ge=0, le=100)
    feedback: str


class AvaliacaoFinal(BaseModel):
    resumo_geral: str
    comunicacao: int = Field(ge=0, le=100)
    tecnico: int = Field(ge=0, le=100)
    confianca: int = Field(ge=0, le=100)
    perguntas: list[AvaliacaoPergunta]
