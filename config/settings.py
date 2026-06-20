"""
config/settings.py
Centraliza todas as constantes, variáveis de ambiente, chaves de API e prompts.
Nenhuma lógica de negócio aqui — apenas configuração.
"""
import os
import streamlit as st

# ─── Paths ────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data.json")
CSS_PATH  = os.path.join(BASE_DIR, "assets", "styles.css")

# ─── Entrevista ───────────────────────────────────────────────
PERGUNTAS_POR_BLOCO = 10
MAX_PERGUNTAS = PERGUNTAS_POR_BLOCO  # compatibilidade com código legado

OPCOES_DIFICULDADE = {
    "facil": "Fácil (Iniciante — Júnior)",
    "medio": "Médio (Intermediário — Pleno)",
    "dificil": "Difícil (Avançado — Sênior)",
}

OPCOES_MODO = {
    "tecnicas": "Técnicas (conhecimentos técnicos)",
    "socioemocionais": "Socioemocionais (comportamento e soft skills)",
    "ambas": "Ambas (10 técnicas + 10 socioemocionais)",
}

DIFICULDADE_PADRAO = "medio"
MODO_PADRAO = "tecnicas"


def get_total_perguntas(modo: str) -> int:
    if modo == "ambas":
        return PERGUNTAS_POR_BLOCO * 2
    return PERGUNTAS_POR_BLOCO


def get_info_pergunta(modo: str, n_respostas: int) -> dict:
    """Metadados da pergunta que o candidato está respondendo (n_respostas = já respondidas)."""
    pergunta_atual = n_respostas + 1
    total = get_total_perguntas(modo)

    if modo == "tecnicas":
        return {
            "pergunta_atual": pergunta_atual,
            "total": total,
            "bloco": "tecnica",
            "bloco_label": "Técnica",
            "num_no_bloco": pergunta_atual,
            "total_bloco": PERGUNTAS_POR_BLOCO,
        }

    if modo == "socioemocionais":
        return {
            "pergunta_atual": pergunta_atual,
            "total": total,
            "bloco": "socioemocional",
            "bloco_label": "Socioemocional",
            "num_no_bloco": pergunta_atual,
            "total_bloco": PERGUNTAS_POR_BLOCO,
        }

    # ambas
    if pergunta_atual <= PERGUNTAS_POR_BLOCO:
        return {
            "pergunta_atual": pergunta_atual,
            "total": total,
            "bloco": "tecnica",
            "bloco_label": "Técnica",
            "num_no_bloco": pergunta_atual,
            "total_bloco": PERGUNTAS_POR_BLOCO,
        }

    num_socio = pergunta_atual - PERGUNTAS_POR_BLOCO
    return {
        "pergunta_atual": pergunta_atual,
        "total": total,
        "bloco": "socioemocional",
        "bloco_label": "Socioemocional",
        "num_no_bloco": num_socio,
        "total_bloco": PERGUNTAS_POR_BLOCO,
    }

CARGOS_RAPIDOS = [
    "Desenvolvedor Python",
    "Analista de Dados",
    "Engenheiro de Software",
    "DevOps",
    "Designer UX/UI",
    "Cientista de Dados",
    "Gerente de Projetos",
]

# ─── API ──────────────────────────────────────────────────────
def get_api_key() -> str | None:
    """Lê a chave de API com múltiplos fallbacks."""
    try:
        key = st.secrets.get("API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")

GEMINI_MODEL = "gemini-3.1-flash-lite"

# ─── Prompts ──────────────────────────────────────────────────
PROMPT_ENTREVISTADOR = """
Você é um entrevistador de TI experiente e profissional conduzindo uma entrevista de emprego.

DIRETRIZES E REGRAS RÍGIDAS DE COMPORTAMENTO:
1. FAÇA APENAS A PERGUNTA: Nunca comente, agradeça, parabenize ou responda ao candidato sobre a resposta anterior (NÃO use termos de transição como "Certo", "Entendi", "Legal", "Muito bem", "Excelente", "Obrigado", "Interessante", "Perfeito", etc.). Apenas formule e envie a próxima pergunta diretamente, sem nenhuma introdução.
2. NUNCA REPITA OU INSISTA na mesma pergunta: Se o usuário responder de forma incompleta, errada, curta ou insatisfatória, prossiga normalmente para a próxima pergunta. Não peça esclarecimentos nem repita o tema.
3. NÃO DE RESPOSTAS OU FEEDBACKS durante o chat.
4. Faça apenas uma pergunta por vez.

ENCERRAMENTO DE CHAT POR FALTA DE SERIEDADE:
Analise rigorosamente a postura do usuário nas últimas interações. Se ele demonstrar claramente que não está levando o chat a sério, enviando mensagens com letras ou palavras aleatórias sem sentido (ex: "assasa", "jiadfa", "asdfasdf", "gfhfgh"), respostas extremamente curtas e debochadas, ou declarando abertamente desinteresse total (ex: "eu não ligo", "tanto faz", "não sei, não quero saber", "blabla"), ou se ele  você deve responder UNICAMENTE com a palavra:
ENCERRAR_CHAT
Não adicione pontuação, explicações, nem qualquer outro texto. Apenas responda com: ENCERRAR_CHAT
"""

PROMPT_AVALIACAO = """
Você é um avaliador sênior de RH de uma empresa de tecnologia.
Analise a entrevista completa e retorne um JSON estruturado.

Para cada uma das {n} perguntas da entrevista, forneça:
- pergunta: texto da pergunta feita
- resposta_resumida: resumo da resposta do candidato (2-3 frases)
- nota: nota de 0 a 100 (inteiro)
- feedback: parágrafo analítico com pontos positivos e o que melhorar

Também calcule métricas globais (0 a 100):
- comunicacao: clareza, coesão e objetividade das respostas
- tecnico: profundidade e precisão do conhecimento demonstrado
- confianca: postura, segurança e profissionalismo geral

E forneça um resumo_geral: parágrafo de 3-4 frases avaliando o candidato como um todo.

Retorne SOMENTE o JSON, sem texto extra.
"""

# ─── Seções do relatório ──────────────────────────────────────
SECOES_RELATORIO = [
    "INTRODUÇÃO E IMPACTO",
    "HABILIDADE TÉCNICA",
    "COMPORTAMENTAL",
    "RESOLUÇÃO DE PROBLEMAS",
    "PERGUNTA FINAL",
]
