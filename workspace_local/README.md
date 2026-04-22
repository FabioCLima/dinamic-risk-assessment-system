# Dynamic Risk Assessment System (Udacity) — Workspace Local

Este diretório (`workspace_local/`) é um **workspace local** para desenvolver e testar o projeto antes de levar para o **Udacity Workspace**.

## Objetivo do Step 1 (Data ingestion)

O `ingestion.py` deve:
- Detectar automaticamente todos os arquivos `.csv` em `input_folder_path` (definido no `config.json`)
- Carregar e concatenar os datasets
- Remover linhas duplicadas
- Salvar `finaldata.csv` em `output_folder_path`
- Salvar `ingestedfiles.txt` em `output_folder_path` (um nome de arquivo por linha)

## Como executar o Step 1 localmente

No Linux/Mac:

```bash
cd workspace_local

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pandas

python ingestion.py
ls -la ingesteddata/
```

Saídas esperadas:
- `ingesteddata/finaldata.csv`
- `ingesteddata/ingestedfiles.txt`

## Observação sobre dependências

O `requirements.txt` do starter é antigo e pode não instalar em Python moderno (ex.: 3.12). Para o Step 1, `pandas` é suficiente. No Udacity Workspace, o ambiente costuma ser compatível com as versões do projeto.

