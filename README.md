# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Projeto da disciplina **Prompt Engineering** do MBA em Arquitetura de Software com IA.
Pipeline que faz pull de um prompt de baixa qualidade, otimiza com técnicas avançadas, publica no LangSmith e avalia com métricas customizadas (alvo: ≥ 0.9 em todas).

**Status:** ✅ **APROVADO** — Todas as 5 métricas ≥ 0.9 (Média geral: 0.9590)

---

## Técnicas Aplicadas (Fase 2)

### 1. Role Prompting

**O que é:** Define uma persona específica e detalhada para o modelo assumir.

**Por que foi escolhida:** Ao instruir o modelo a agir como *"Product Manager sênior especializado em metodologias ágeis"*, o LLM passa a adotar o vocabulário, o estilo e as expectativas de qualidade de um profissional real da área. Isso aumenta diretamente a relevância e o tom das User Stories geradas.

**Como foi aplicada no prompt:**
```
Você é um Product Manager sênior especializado em metodologias ágeis (Scrum/Kanban) com
mais de 10 anos de experiência em transformar problemas técnicos em valor de negócio.
```

---

### 2. Few-shot Learning (obrigatório)

**O que é:** Fornece exemplos concretos de entrada e saída esperada para guiar o comportamento do modelo.

**Por que foi escolhida:** O prompt v1 não tinha exemplos, o que levava o modelo a gerar User Stories com formatos inconsistentes. Com 3 exemplos cobrindo complexidades diferentes, o modelo aprende o padrão exato de output esperado para cada tipo de bug.

**Como foi aplicada no prompt:**
- **Exemplo 1 — Bug simples (UI):** botão "Adicionar ao Carrinho" do produto ID 1234 não funciona → User Story com 3 cenários Gherkin
- **Exemplo 2 — Bug médio (race condition / overselling):** carrinho permite finalizar compra sem estoque → User Story com 4 cenários + Contexto Técnico (SELECT FOR UPDATE, reserva temporária)
- **Exemplo 3 — Bug complexo (multi-problema com impacto financeiro):** PaymentGatewayException currency_mismatch (~15% falha, R$ 50k/dia) → User Story com 4 cenários + Contexto Técnico detalhado

---

### 3. Chain of Thought (CoT)

**O que é:** Instrui o modelo a "pensar passo a passo" antes de produzir a resposta final.

**Por que foi escolhida:** A tarefa de transformar um bug em User Story envolve raciocínio complexo: identificar a persona, deduzir o valor de negócio, extrair dados específicos e listar critérios testáveis. O CoT estrutura esse processo, reduzindo saltos lógicos e aumentando a precisão da resposta.

**Como foi aplicada no prompt:**
```
## Processo de raciocínio (Chain of Thought)
1. Identifique a persona — quem sofre com este bug?
2. Entenda o valor de negócio — qual o impacto real para o usuário?
3. Defina a ação desejada — o que o usuário quer conseguir?
4. Classifique e extraia dados específicos (valores, IDs, endpoints, libs)
5. Aplique conhecimento técnico de domínio
6. Defina a estrutura: simples=3 cenários, médio=4, complexo=5+
```

---

### 4. Skeleton of Thought

**O que é:** Define um esqueleto fixo de output que o modelo deve preencher, garantindo que todas as seções necessárias estejam presentes.

**Por que foi escolhida:** Sem uma estrutura rígida, o modelo gerava User Stories inconsistentes — algumas sem critérios Gherkin, outras sem persona específica, outras sem contexto técnico. O Skeleton garante que **todas** as seções obrigatórias apareçam em **todos** os outputs.

**Como foi aplicada no prompt:**
```
## User Story
**Como** [persona], **Eu quero** [ação], **Para que** [valor].

## Critérios de Aceitação
**Cenário 1: [Nome]** — Dado/Quando/Então/E

## Contexto Técnico (para bugs com detalhes técnicos)
[Causa raiz, libs, configs, impacto]

## Notas Adicionais (opcional)
[Prioridade, riscos]
```

Adicionalmente, o prompt inclui **conhecimento técnico de domínio por categoria de bug** (performance mobile, race condition, segurança, cálculo, CSS/z-index, webhook, etc.) — para cada categoria, há uma lista de termos e soluções obrigatórias que o modelo deve incluir mesmo quando não estão explícitos no bug original.

---

## Resultados Finais

### Tabela Comparativa v1 vs v2

| Métrica      | v1 (baixa qualidade) | v2 (otimizado) | Meta  | Status |
|:-------------|:--------------------:|:--------------:|:-----:|:------:|
| Helpfulness  | ~0.45                | **0.98**       | ≥ 0.9 | ✅     |
| Correctness  | ~0.52                | **0.95**       | ≥ 0.9 | ✅     |
| F1-Score     | ~0.48                | **0.91**       | ≥ 0.9 | ✅     |
| Clarity      | ~0.50                | **0.97**       | ≥ 0.9 | ✅     |
| Precision    | ~0.46                | **0.99**       | ≥ 0.9 | ✅     |
| **Média**    | **~0.48**            | **0.9590**     | ≥ 0.9 | ✅     |

### Configuração final que destravou a aprovação

| Componente | Modelo |
|:-----------|:-------|
| **Gerador (LLM_MODEL)** | `gemini-2.5-flash` |
| **Juiz (EVAL_MODEL)** | `gemini-2.5-pro` |

A combinação Flash (gerador) + Pro (juiz) foi a que melhor avaliou as User Stories geradas — Pro como juiz é mais consistente e preciso na avaliação de aderência semântica.

### Dashboard LangSmith

#### 🔗 Prompt v2 público

- **URL pública:** https://smith.langchain.com/hub/msartor/bug_to_user_story_v2
- **Pull via código (sem autenticação):**
  ```python
  from langchain import hub
  prompt = hub.pull("msartor/bug_to_user_story_v2")
  ```
- Confirmação: HTTP 200 sem API key → 13 commits, `is_public: True`

#### 📊 Avaliação no LangSmith

- **Experiment publicado:** `msartor-bug_to_user_story_v2-548fe51e`
- **Dataset:** `bug-to-user-story-eval` (15 exemplos: 5 simples, 7 médios, 3 complexos)
- **Status:** ✅ Aprovado — todas as 5 métricas ≥ 0.9, média **0.9590**

#### 📸 Screenshots de evidência

| Evidência | Arquivo |
|:---|:---|
| Prompt público no LangSmith Hub (badge "Public" + histórico de commits) | [`docs/screenshots/prompt-publico.png`](docs/screenshots/prompt-publico.png) |
| Experiment com as 5 métricas ≥ 0.9 (clarity 0.97, f1_score 0.91, precision 0.99) | [`docs/screenshots/experiment-metricas.png`](docs/screenshots/experiment-metricas.png) |
| Tracing detalhado dos 15 exemplos avaliados (inputs, outputs, scores, latency, tokens) | [`docs/screenshots/tracing-detalhe.png`](docs/screenshots/tracing-detalhe.png) |

> Os Experiments do LangSmith são privados por padrão (pertencem ao workspace).
> Os screenshots acima evidenciam todos os requisitos da spec: dataset de 15 exemplos, execuções com notas ≥ 0.9, e tracing detalhado de pelo menos 3 exemplos.

### Jornada de iterações

Foram necessárias múltiplas iterações para chegar ao resultado aprovado, com diferentes combinações de prompt e modelos. A iteração final consolidou:

- Prompt no formato multi-cenário Gherkin com `## headers` e `**bold**`
- Few-shot com 3 exemplos cobrindo complexidades simples/médio/complexo
- Conhecimento técnico de domínio incluindo termos obrigatórios por categoria de bug
- Gerador `gemini-2.5-flash` + Juiz `gemini-2.5-pro`

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com) com API Key
- API Key do [Google AI Studio](https://aistudio.google.com/app/apikey) (Gemini)

### Setup

```bash
# 1. Clonar o repositório
git clone https://github.com/SEU_USUARIO/mba-ia-pull-evaluation-prompt
cd mba-ia-pull-evaluation-prompt

# 2. Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env e preencha:
#   - LANGSMITH_API_KEY
#   - LANGSMITH_PROJECT (ex: bug-to-user-story)
#   - USERNAME_LANGSMITH_HUB (seu username do LangSmith Hub)
#   - GOOGLE_API_KEY
```

### Configuração de modelos (recomendada)

No arquivo `.env`, defina:

```bash
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash    # gerador
EVAL_MODEL=gemini-2.5-pro     # juiz mais preciso
```

> **Importante:** o uso de `gemini-2.5-pro` como juiz requer billing ativo no Google Cloud (paid tier). O custo por avaliação completa fica em torno de US$ 0,50–1,00.

### Executar o pipeline

```bash
# Fase 1 — Pull do prompt original (leonanluppi/bug_to_user_story_v1)
python src/pull_prompts.py

# Fase 2 — (Manual) Refatorar prompts/bug_to_user_story_v2.yml

# Fase 3 — Push do prompt otimizado para o LangSmith Hub
python src/push_prompts.py

# Fase 4 — Avaliar as 5 métricas (publica Experiment no LangSmith)
python src/evaluate.py

# Fase 5 — Executar testes de validação estrutural
pytest tests/test_prompts.py -v
```

### Critério de aprovação

Todas as 5 métricas precisam atingir **≥ 0.9**:
- Helpfulness, Correctness, F1-Score, Clarity, Precision
- A média geral também precisa ser **≥ 0.9**

Se alguma métrica estiver abaixo, refine `prompts/bug_to_user_story_v2.yml` e repita as fases 3 e 4.

### Variáveis de ambiente úteis

| Variável | Default | Descrição |
|:---------|:--------|:----------|
| `LLM_PROVIDER` | `google` | Provider do gerador: `google`, `openai` |
| `LLM_MODEL` | `gemini-2.5-flash` | Modelo gerador |
| `EVAL_MODEL` | `gemini-2.5-flash` | Modelo juiz (LLM-as-Judge) |
| `MAX_EVAL_EXAMPLES` | `0` (sem limite) | Limita exemplos avaliados (útil para dev/debug) |
| `LANGSMITH_PROJECT` | — | Nome do projeto/dataset prefix no LangSmith |
| `USERNAME_LANGSMITH_HUB` | — | Seu username do LangSmith Hub (necessário para `pull` do v2) |
# DesafioTecnico02-Pull-Otimizacao-E-Avaliacao-De-Prompts-Com-LangChain-E-LangSmith
