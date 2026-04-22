# Project Design — Dynamic Risk Assessment System (Udacity)

Este documento descreve as principais **decisões técnicas** (como em um *code review*) do projeto **Dynamic Risk Assessment System**, para alguém que está chegando agora e não conhece o código.

O objetivo do projeto é manter um pipeline simples e automatizável para:
1) ingerir novos dados, 2) treinar e avaliar um modelo, 3) “deployar” artefatos, 4) expor métricas/diagnósticos via API e relatórios, e 5) automatizar reexecuções quando houver dados novos e/ou alteração de performance (drift).

---

## 1) Visão geral da arquitetura

O projeto é organizado em **scripts** (estilo *batch pipeline*) que se comunicam por **artefatos em disco** (CSV/TXT/PKL/PNG) e por um **serviço HTTP** (Flask) para consulta de resultados.

Pilares do design:
- **Configuração central** em `config.json` (evita caminhos hard-coded).
- **Contratos simples** de entrada/saída por arquivo (facilita depuração e avaliação).
- **Idempotência**: rodar o mesmo script duas vezes deve sobrescrever os artefatos de forma segura.
- **Portabilidade**: paths resolvidos relativos à pasta do projeto (compatível com Udacity Workspace).

---

## 2) Estrutura de pastas (workspace_local)

A pasta `workspace_local/` é um “workspace” local espelhando o starter da Udacity, com os scripts e diretórios esperados:

- `config.json`: define onde ler/gravar dados, modelos e deploy.
- `sourcedata/`: dados “reais” de treino (no modo final do projeto).
- `testdata/`: dados de teste (ex.: `testdata.csv`).
- `ingesteddata/`: saídas do Step 1 (`finaldata.csv`, `ingestedfiles.txt`).
- `models/`: artefatos do Step 2/4 (modelo, score, plots, apireturns…).
- `production_deployment/`: artefatos “deployados” (cópia do modelo/score/ingestedfiles).

Decisão: manter `production_deployment/` como “fonte de verdade” do que está em produção, porque a API e diagnósticos precisam sempre apontar para o modelo ativo (deployado).

---

## 3) Configuração (config.json) e “modo final”

O projeto é **dirigido por configuração**:

- `input_folder_path`: onde procurar dados novos para ingestão (`sourcedata/` no final).
- `output_folder_path`: onde salvar `finaldata.csv` e `ingestedfiles.txt` (`ingesteddata/`).
- `test_data_path`: onde ler `testdata.csv` (`testdata/`).
- `output_model_path`: onde salvar `trainedmodel.pkl` e `latestscore.txt` (no final: `models/`).
- `prod_deployment_path`: onde copiar os artefatos deployados (`production_deployment/`).

Decisão: alternar “practice” (`practicedata/`, `practicemodels/`) para “final” (`sourcedata/`, `models/`) é feito **apenas alterando `config.json`**, sem precisar mudar o código.

---

## 4) Ambiente Python (reprodutibilidade)

O ambiente do projeto é gerenciado com `uv` em `workspace_local/.venv`:
- Usamos **Python 3.9.x** para compatibilidade com as versões fixas em `requirements.txt` (pinned e antigas).
- Instalamos dependências com `uv pip install -r requirements.txt`.

Decisões:
- **Pinagem** via `requirements.txt` prioriza compatibilidade com o projeto Udacity (em vez de “latest”).
- Evitamos `from __future__ import annotations` porque pode causar problemas em alguns ambientes/avaliadores.

---

## 5) Step 1 — Ingestion (`ingestion.py`)

### O que faz
Lê todos os CSVs dentro de `input_folder_path`, concatena, remove duplicatas e salva:
- `ingesteddata/finaldata.csv`
- `ingesteddata/ingestedfiles.txt` (um filename por linha)

### Decisões técnicas
- **Auto-descoberta** de arquivos (`*.csv`) para suportar variação na quantidade e nome dos datasets.
- **Deduplicação** (`drop_duplicates`) para evitar que o conjunto final cresça com linhas repetidas ao longo do tempo.
- **`pathlib.Path`** para manipular caminhos de forma mais robusta e legível.
- Função retorna `(DataFrame, filenames)` para reuso futuro (automação/validação), mas o contrato principal são os arquivos em disco.

---

## 6) Step 2 — Training/Scoring/Deploy

### 6.1 Treinamento (`training.py`)
Treina um `LogisticRegression` usando as features numéricas:
- `lastmonth_activity`, `lastyear_activity`, `number_of_employees`

Decisões:
- `corporation` é um identificador e é **excluído** de features.
- `random_state=0` para reprodutibilidade.
- `max_iter=1000` para reduzir risco de não convergir em ambientes diferentes.

Artefato:
- `models/trainedmodel.pkl`

### 6.2 Scoring (`scoring.py`)
Avalia F1 score no `testdata/testdata.csv`.

Decisões:
- Métrica F1 por ser padrão do enunciado e útil em problemas binários com potencial desbalanceamento.
- O score é gravado em texto simples (um número por linha), fácil de ler e comparar.

Artefato:
- `models/latestscore.txt`

### 6.3 Deploy (`deployment.py`)
Não treina nem reavalia; apenas copia artefatos para produção:
- `trainedmodel.pkl`, `latestscore.txt`, `ingestedfiles.txt` → `production_deployment/`

Decisões:
- `shutil.copy2` para preservar metadados e facilitar auditoria (timestamps).
- Operação é **idempotente**: reexecução sobrescreve os mesmos arquivos.

---

## 7) Step 3 — Diagnostics (`diagnostics.py`)

O diagnóstico é dividido em funções reutilizáveis (não apenas “script”):

1. `model_predictions(dataset: DataFrame) -> List[int]`
   - Lê **modelo deployado** em `production_deployment/trainedmodel.pkl`
   - Retorna lista de predições com mesmo tamanho da entrada

2. `dataframe_summary() -> List[float]`
   - Calcula média/mediana/desvio padrão para colunas numéricas do `finaldata.csv`

3. `missing_data() -> List[float]`
   - Percentual de NA por coluna

4. `execution_time() -> List[float]`
   - Mede tempo de `ingestion.py` e `training.py` chamando os scripts via subprocess

5. `outdated_packages_list() -> List[Dict]`
   - Usa `pip list --format=json` e `pip list --outdated --format=json`
   - Compara instalado vs “latest” (não altera o ambiente)

Decisões:
- Diagnósticos apontam para o **modelo deployado** (produção), para refletir exatamente o que a API está servindo.
- O “timing” mede execução real dos scripts (mais representativo do que medir apenas chamadas internas).

---

## 8) Step 4 — Reporting + API

### 8.1 Reporting (`reporting.py`)
Gera uma matriz de confusão usando:
- `testdata/testdata.csv` como ground truth
- `diagnostics.model_predictions` para predições do modelo deployado

Artefato:
- `models/confusionmatrix.png`

Decisões:
- O plot usa `seaborn.heatmap` por legibilidade e simplicidade.
- O modelo é sempre o deployado para evitar divergência “treinado localmente vs em produção”.

### 8.2 API (`app.py`)
API Flask com endpoints:
- `POST /prediction`: recebe JSON com `filepath` (relativo ou absoluto) e retorna predições
- `GET /scoring`: retorna o F1 (rodando `scoring.score_model()`)
- `GET /summarystats`: retorna estatísticas do Step 3
- `GET /diagnostics`: retorna timing, NA%, dependências

Decisões:
- Todas as rotas retornam **HTTP 200** conforme exigência do enunciado (inclusive em erro, retornando `{"error": ...}`).
- Porta configurável por variável de ambiente `APP_PORT` (evita conflitos em ambientes compartilhados).

### 8.3 Chamadas de API (`apicalls.py`)
Chama os endpoints e grava:
- `models/apireturns.txt`

Decisões:
- Implementação usa `urllib` (stdlib) para reduzir dependência de bibliotecas externas e manter o script “leve”.
- Se a API não estiver rodando, o script **sobe uma instância local** temporária e derruba ao final.

---

## 9) Step 5 — Automação (`fullprocess.py`) e cron

`fullprocess.py` orquestra o fluxo:
1. Detecta arquivos novos em `sourcedata/` comparando com `production_deployment/ingestedfiles.txt`
2. Se não houver novos dados: encerra
3. Se houver: roda `ingestion.py` → `training.py` → `scoring.py`
4. Lê `deployed_score` de `production_deployment/latestscore.txt`
5. Deploy **somente se** `candidate_score > deployed_score` (ou se `deployed_score is None`, caracterizando deploy inicial). Após o deploy, gera `confusionmatrix2.png` e `apireturns2.txt`.

Artefatos do Step 5:
- `models/confusionmatrix2.png`
- `models/apireturns2.txt`
- `cronjob.txt` (linha do cron a cada 10 minutos)

Decisões e justificativas:
- **New data check** por filenames é simples e suficiente para o escopo do projeto.
- Regra de drift / gate de deploy: seguindo estritamente a rubrica (Seção 5), o deploy só ocorre quando o modelo candidato **supera** o modelo em produção (`candidate_score > deployed_score`). Score igual ou pior não dispara redeploy. Em produção, essa regra pode ser refinada (limiar, janela temporal, métricas adicionais).
- A API usada no Step 5 também respeita `APP_PORT`, evitando conflito.

---

## 10) Standout suggestions (opcionais)

As sugestões opcionais foram documentadas em `standout_suggestion_optional.md` (na raiz do repositório), e incluem:
- PDF report com métricas/plots
- Histórico de diagnósticos (tendências no tempo)
- Persistência em banco SQL (em vez de CSV/TXT)

---

## 11) Limitações conhecidas e próximos passos

- **Sem pipeline de features**: o projeto assume features já limpas e numéricas (exceto `corporation`).
- **Drift simplificado**: comparação direta de F1 é didática; em produção usaríamos thresholds, significância, e monitoramento contínuo.
- **Artefatos em disco**: suficiente para o projeto, mas em produção poderíamos versionar artefatos (MLflow/DVC) e usar storage externo.
- **API de desenvolvimento**: Flask built-in serve apenas para dev; para produção usar `gunicorn`/`wsgi.py`.

Se você está começando agora, o caminho recomendado para entender o projeto é:
1) ler `config.json`, 2) rodar `ingestion.py`, 3) rodar `training.py`/`scoring.py`/`deployment.py`, 4) rodar `reporting.py`, 5) iniciar `app.py`, 6) rodar `apicalls.py`, 7) rodar `fullprocess.py`.

