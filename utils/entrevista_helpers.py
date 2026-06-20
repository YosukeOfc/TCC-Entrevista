"""
utils/entrevista_helpers.py
Helpers para montar contexto de prompts da entrevista.
"""
from config.settings import OPCOES_DIFICULDADE, OPCOES_MODO, get_info_pergunta

_INSTRUCOES_DIFICULDADE = {
    "facil": (
        "Nível JÚNIOR: perguntas introdutórias, conceitos fundamentais, "
        "situações simples do dia a dia. Evite jargões avançados ou cenários muito complexos."
    ),
    "medio": (
        "Nível PLENO: perguntas intermediárias, experiência prática, "
        "problemas reais de projetos e trade-offs comuns na área."
    ),
    "dificil": (
        "Nível SÊNIOR: perguntas avançadas, arquitetura, liderança técnica, "
        "cenários complexos, decisões estratégicas e profundidade de conhecimento."
    ),
}

_INSTRUCOES_BLOCO = {
    "tecnica": (
        "Faça APENAS perguntas TÉCNICAS sobre conhecimentos, ferramentas, "
        "metodologias, código, infraestrutura e competências hard skills da vaga."
    ),
    "socioemocional": (
        "Faça APENAS perguntas SOCIOEMOCIONAIS/COMPORTAMENTAIS: soft skills, "
        "trabalho em equipe, comunicação, conflitos, liderança, adaptabilidade "
        "e situações do método STAR."
    ),
}


def montar_instrucao_entrevista(
    vaga: str,
    dificuldade: str,
    modo: str,
    n_respostas: int,
) -> str:
    """Monta system instruction com vaga, dificuldade, modo e bloco atual."""
    from config.settings import PROMPT_ENTREVISTADOR

    info = get_info_pergunta(modo, n_respostas)
    diff_label = OPCOES_DIFICULDADE.get(dificuldade, dificuldade)
    modo_label = OPCOES_MODO.get(modo, modo)

    bloco_extra = ""
    if modo == "ambas" and info["bloco"] == "socioemocional" and info["num_no_bloco"] == 1:
        bloco_extra = (
            "\nATENÇÃO: O bloco técnico (10 perguntas) foi concluído. "
            "A partir de agora, faça SOMENTE perguntas socioemocionais/comportamentais.\n"
        )
    elif modo == "ambas" and info["bloco"] == "tecnica" and info["num_no_bloco"] == 1:
        bloco_extra = (
            "\nATENÇÃO: Inicie o bloco TÉCNICO. "
            "Faça SOMENTE perguntas técnicas até completar este bloco.\n"
        )

    return (
        f"{PROMPT_ENTREVISTADOR}\n\n"
        f"CONTEXTO DESTA ENTREVISTA:\n"
        f"- Vaga: {vaga}\n"
        f"- Nível de dificuldade: {diff_label}\n"
        f"- Modo de entrevista: {modo_label}\n"
        f"- Bloco atual: {info['bloco_label']} "
        f"(pergunta {info['num_no_bloco']} de {info['total_bloco']} neste bloco)\n"
        f"- Progresso geral: pergunta {info['pergunta_atual']} de {info['total']}\n\n"
        f"INSTRUÇÕES DE DIFICULDADE:\n{_INSTRUCOES_DIFICULDADE.get(dificuldade, '')}\n\n"
        f"INSTRUÇÕES DO BLOCO ATUAL:\n{_INSTRUCOES_BLOCO[info['bloco']]}\n"
        f"{bloco_extra}"
    )


def montar_instrucao_avaliacao(vaga: str, dificuldade: str, modo: str, n_perguntas: int) -> str:
    from config.settings import PROMPT_AVALIACAO

    diff_label = OPCOES_DIFICULDADE.get(dificuldade, dificuldade)
    modo_label = OPCOES_MODO.get(modo, modo)
    base = PROMPT_AVALIACAO.replace("{n}", str(n_perguntas))
    return (
        f"{base}\n\n"
        f"Contexto da entrevista:\n"
        f"- Vaga: {vaga}\n"
        f"- Nível: {diff_label}\n"
        f"- Modo: {modo_label}\n"
    )
