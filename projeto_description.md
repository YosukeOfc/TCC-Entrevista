# Documentação do Projeto: **InterviewAI**

O **InterviewAI** é uma plataforma interativa de simulação de entrevistas de emprego na área de tecnologia. Desenvolvido para servir como Trabalho de Conclusão de Curso (TCC), o sistema utiliza inteligência artificial generativa de ponta (Google Gemini) para simular entrevistadores reais, conduzir o candidato através de perguntas técnicas e comportamentais personalizadas, e fornecer uma avaliação detalhada de desempenho.

---

## 🎯 Objetivos do Sistema
- **Simulação Realista**: Criar um ambiente imersivo onde o candidato responde a perguntas sob medida baseadas no cargo selecionado.
- **Avaliação de Hard e Soft Skills**: Medir o desempenho do candidato em aspectos técnicos (precisão das respostas), de comunicação (clareza e articulação) e profissionalismo.
- **Feedback Construtivo**: Apresentar um diagnóstico detalhado com notas individuais por pergunta, médias agregadas por competência e sugestões de melhoria.

---

## 🛠️ Stack Tecnológica
- **Linguagem Principal**: [Python 3.13+](https://www.python.org/)
- **Interface Gráfica (Frontend/Backend integrado)**: [Streamlit](https://streamlit.io/) (Framework open-source para criação rápida de aplicativos web interativos).
- **Provedor de IA**: [Google GenAI SDK](https://github.com/google/generative-ai-python) (API oficial do Google Gemini).
- **Modelo de IA Utilizado**: `gemini-3.1-flash-lite` (Otimizado para tempo de resposta rápido e baixo custo operacional).
- **Estilização Visual**: CSS Customizado em folha externa (`assets/styles.css`) injetado via código para garantir um visual moderno e responsivo.
- **Validação de Schemas**: [Pydantic v2](https://docs.pydantic.dev/) para garantir integridade na estruturação da resposta em formato JSON vinda da IA.

---

## 🏗️ Arquitetura e Organização de Pastas
O projeto segue uma arquitetura modular inspirada nos padrões de mercado (ex: MVC / Clean Architecture), dividindo claramente responsabilidades entre persistência de dados, lógica de estados, serviços de IA e componentes de interface:

```
TCCFINAL/
│
├── main.py                    # Ponto de entrada do Streamlit, gerencia roteamento global
│
├── config/
│   └── settings.py            # Constantes, caminhos de arquivos, chaves e prompts da IA
│
├── core/
│   ├── state.py               # Centralizador de estado (Session State). Sem comandos de UI
│   └── persistence.py         # Leitura/escrita estruturada no arquivo data.json
│
├── services/
│   └── gemini_service.py      # Integração limpa com a API do Gemini (funções puras)
│
├── models/
│   └── schemas.py             # Modelos Pydantic para validação das respostas da IA
│
├── ui/
│   ├── header.py              # Cabeçalho global das telas
│   ├── sidebar.py             # Menu lateral, progresso da entrevista e entrada de chaves API
│   └── pages/
│       ├── selecao.py         # Tela 1: Seleção do cargo e ativação de chave API
│       ├── confirmacao.py     # Tela 2: Apresentação da vaga e regras antes de iniciar
│       ├── entrevista.py      # Tela 3: Chat com perguntas da IA e caixa de respostas
│       ├── relatorio.py       # Tela 4: Painel de notas com gauges e feedbacks por pergunta
│       ├── historico.py       # Tela 5: Lista de sessões concluídas salvas localmente
│       └── pendencias.py      # Tela 6: Recuperação e retomada de entrevistas interrompidas
│
├── utils/
│   └── helpers.py             # Funções de auxílio (Geração de gauges SVG, estrelas de classificação)
│
├── assets/
│   └── styles.css             # Arquivo CSS centralizador de estilo
│
└── data.json                  # Banco de dados local baseado em JSON
```

---

## 📋 Funcionalidades Principais

### 1. Seleção Inteligente de Cargo
O usuário pode selecionar um cargo padrão da lista rápida (ex: *Desenvolvedor Python*, *Cientista de Dados*, *UX/UI Designer*) ou digitar o cargo de interesse. A IA gerará um roteiro customizado focado exatamente nessa profissão.

### 2. Fluxo da Entrevista Adaptativo (Até 10 Perguntas)
- A barra lateral monitora o progresso atual do candidato de 1 a 10.
- A IA varia a natureza das perguntas entre conhecimento prático e comportamento (método STAR).
- **Comunicação Direta**: O entrevistador foca unicamente na pergunta seguinte, eliminando preâmbulos redundantes ("Certo", "Muito bem", "Obrigado") para aproximar o simulador de uma entrevista técnica autêntica.
- **Tolerância a Respostas Ruins**: Caso o usuário responda de forma insuficiente ou pule a pergunta, a IA avança normalmente sem repetir a pergunta, guardando a observação para a avaliação.

### 3. Detecção de Falta de Seriedade (Anti-Spam)
O prompt conta com regras de proteção. Se o usuário insistir em respostas contendo apenas caracteres aleatórios (ex: `"assasa"`, `"jiadfa"`) ou declarações de desdém, a IA retorna o comando reservado `ENCERRAR_CHAT`. O sistema intercepta o sinal, interrompe o fluxo imediatamente e envia as respostas atuais para o avaliador, rotulando a entrevista como "Encerrada Precocemente por falta de seriedade".

### 4. Resiliência do Estado (Recuperação de Falhas e F5)
- **F5 Seguro**: Ao atualizar a página, o usuário não perde o histórico de entrevistas inacabadas. O app abre limpo na tela inicial, mas salva a sessão antiga na tela de **Pendências**.
- **Página de Pendências**: Lista entrevistas inacabadas mostrando o cargo correspondente e a quantidade de perguntas respondidas. O usuário pode **Retomar** do ponto exato onde parou ou **Excluir** a sessão do histórico.
- **Tolerância a Quedas de Rede**: Se a conexão de rede ou a API Gemini falharem no envio de uma resposta, a aplicação mantém a resposta do candidato no campo de texto e renderiza um alerta estático. O usuário pode clicar em enviar novamente, evitando perda de dados ou a sensação de que o app "travou" na mesma pergunta.

### 5. Painel de Desempenho e Histórico
- **Gauges Interativos**: Representações circulares dinâmicas das notas de Comunicação, Habilidade Técnica e Confiança (geradas dinamicamente via SVGs leves).
- **Feedback Individualizado**: Avaliação minuciosa de cada resposta do candidato contendo nota de 0 a 100 e pontos positivos/de melhoria.
- **Exportação de Relatório**: Permite baixar todo o relatório detalhado em arquivo de texto plano (`.txt`) com um clique.
- **Histórico**: Acesso a qualquer entrevista concluída anteriormente.

---

## 🧠 Engenharia de Prompts (Prompt Engineering)

O projeto faz uso de duas diretrizes estruturais de prompt enviadas à API do Gemini em formato de `system_instruction`:

1. **Prompt do Entrevistador (`PROMPT_ENTREVISTADOR`)**:
   Instrui o modelo a agir estritamente como um profissional de RH especializado em tecnologia. Define as regras de alternância de temas, tom profissional e impessoal (sem preâmbulos e transições), avanço direto em respostas evasivas, e a lógica de gatilho para o comando `ENCERRAR_CHAT`.

2. **Prompt do Avaliador (`PROMPT_AVALIACAO`)**:
   Ativa o modo de inteligência analítica. O avaliador lê a transcrição da entrevista e devolve um JSON com validação estrita (composto por resumo geral do candidato, notas agregadas e a lista de feedbacks estruturada). A estrutura é mapeada diretamente na interface através do Pydantic.
