# PRD — AI Interview Simulator (Streamlit + Python)

## 1. Visão do Produto
Aplicação em Streamlit que simula entrevistas de emprego usando IA, permitindo que o usuário treine respostas, receba feedback e evolua em diferentes áreas profissionais.

## 2. Problema
Pessoas que vão para entrevistas geralmente:
- não sabem o que esperar
- travam ao responder perguntas
- não conseguem estruturar respostas bem
- não recebem feedback realista

O sistema resolve isso simulando entrevistas realistas com IA.

## 3. Público-alvo
- Estudantes procurando estágio
- Júnior devs
- Pessoas mudando de carreira
- Qualquer um que entra em pânico com “fale sobre você”

## 4. Proposta de Valor
Simular entrevistas reais com:
- perguntas personalizadas por área
- feedback detalhado da IA
- avaliação de desempenho
- evolução do usuário ao longo do tempo

## 5. Funcionalidades principais

### 5.1 Simulação de entrevista
IA gera perguntas baseadas em:
- área
- stack

### 5.2 Respostas do usuário
Usuário responde perguntas em formato texto.

### 5.3 Feedback da IA
Após cada resposta:
- nota (0–10)
- pontos fortes
- pontos fracos
- melhorias

### 5.4 Nota final
Avaliação geral da entrevista:
- comunicação
- técnica
- confiança

### 5.5 Histórico em JSON
Armazena:
- perguntas
- respostas
- feedback
- nota final

### 5.6 Modo treino
- entrevista completa
- só técnico
- só comportamental

## 6. IA no sistema
Responsável por:
- gerar perguntas
- simular entrevistador
- avaliar respostas
- adaptar dificuldade

## 7. Tecnologia
- Streamlit (frontend)
- Python (lógica)
- JSON (persistência)

## 8. Estrutura
- app.py
- interview_engine.py
- storage.py
- /data

## 9. Fluxo
1. Usuário escolhe vaga
2. IA gera perguntas
3. Usuário responde
4. IA avalia
5. Salva em JSON

## 10. MVP
- 5 perguntas
- feedback simples
- salvar JSON

