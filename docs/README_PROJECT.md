# Dynamic Risk Assessment System

Projeto de MLOps da Udacity para criar um pipeline completo de:

- ingestão de dados
- treinamento e scoring de modelo
- deploy de artefatos
- diagnósticos e reporting
- automação por cron

Este diretório contém o `workspace_local/`, a cópia de trabalho usada para desenvolver, testar e validar o projeto antes de levar para o ambiente da Udacity.

## Visão geral

O objetivo do sistema é estimar o risco de evasão (`exited`) de clientes corporativos e manter o modelo atualizado ao longo do tempo.

O fluxo principal é:

1. Ingerir dados novos
2. Treinar um modelo `LogisticRegression`
3. Calcular F1 score
4. Publicar os artefatos em produção
5. Gerar diagnóstico e relatório
6. Automatizar tudo com `fullprocess.py`

## Estrutura do projeto

- `config.json`: caminhos de entrada e saída do pipeline
- `ingestion.py`: junta CSVs e gera `finaldata.csv`
- `training.py`: treina o modelo e salva `trainedmodel.pkl`
- `scoring.py`: calcula e salva `latestscore.txt`
- `deployment.py`: copia os artefatos para `production_deployment/`
- `diagnostics.py`: estatísticas, NA%, timing e dependências
- `reporting.py`: gera `confusionmatrix.png`
- `app.py`: API Flask com endpoints do projeto
- `apicalls.py`: consome a API e salva `apireturns.txt`
- `fullprocess.py`: orquestra o pipeline completo
- `dbsetup.py`: cria a base SQLite de histórico
- `archive_diagnostics.py`: arquiva artefatos antigos para análise temporal

## Artefatos esperados

### Step 1

- `ingesteddata/finaldata.csv`
- `ingesteddata/ingestedfiles.txt`

### Step 2

- `models/trainedmodel.pkl`
- `models/latestscore.txt`

### Step 3

- Saídas de diagnósticos no console e/ou artefatos de suporte

### Step 4

- `models/confusionmatrix.png`
- `models/apireturns.txt`

### Step 5

- `models/confusionmatrix2.png`
- `models/apireturns2.txt`
- `cronjob.txt`

### Standouts opcionais

- `models/report.pdf`
- `olddiagnostics/`
- `ingesteddata/pipeline_history.sqlite`

## Requisitos

- Python 3.9.x
- `uv`
- Dependências do `requirements.txt`

## Como executar o projeto

### 1. Criar e preparar o ambiente

```bash
cd /home/fabiolima/Desktop/MLOps_Projects/Dinamic_Risk_Assessment_System/workspace_local
uv venv -c --seed --python 3.9 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

### 2. Ativar o ambiente

```bash
source .venv/bin/activate
```

### 3. Rodar o pipeline base

```bash
python ingestion.py
python training.py
python scoring.py
python deployment.py
python diagnostics.py
python reporting.py
```

### 4. Subir a API

Use uma porta livre. Se a 8000 estiver ocupada:

```bash
APP_PORT=8001 python app.py
```

### 5. Consumir a API

Em outro terminal:

```bash
APP_PORT=8001 python apicalls.py
```

### 6. Rodar a automação completa

```bash
APP_PORT=8001 python fullprocess.py
```

## Como verificar se tudo foi criado

### Verificar Step 1

```bash
ls -la ingesteddata/
```

Você deve ver:

- `finaldata.csv`
- `ingestedfiles.txt`

### Verificar Step 2

```bash
ls -la models/
```

Você deve ver:

- `trainedmodel.pkl`
- `latestscore.txt`

### Verificar deploy

```bash
ls -la production_deployment/
```

Você deve ver:

- `trainedmodel.pkl`
- `latestscore.txt`
- `ingestedfiles.txt`

### Verificar reporting e API

```bash
ls -la models/
```

Procure por:

- `confusionmatrix.png`
- `apireturns.txt`
- `confusionmatrix2.png`
- `apireturns2.txt`
- `report.pdf` se o standout opcional estiver ativo

### Verificar cron job

```bash
cat cronjob.txt
```

## Como a API funciona

O projeto expõe endpoints Flask para consulta dos resultados do pipeline.

- `POST /prediction`
- `GET /scoring`
- `GET /summarystats`
- `GET /diagnostics`

O endpoint `/prediction` recebe um JSON com o caminho do arquivo de entrada, por exemplo:

```json
{"filepath": "testdata/testdata.csv"}
```

## Observações importantes

- O projeto usa `config.json` para manter os caminhos centralizados.
- O fluxo foi desenhado para funcionar no `workspace_local/` e também no ambiente da Udacity.
- Os scripts suportam CLIs com `argparse`, preservando os valores padrão quando nenhum argumento é passado.
- Os artefatos opcionais de standout foram adicionados para enriquecer a entrega, mas não são obrigatórios na rubrica base.

## Próximo passo

Se você quiser, eu também posso montar uma versão mais curta desse README para servir como `README.md` principal do repositório.
