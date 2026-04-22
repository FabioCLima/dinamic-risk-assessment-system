# Rubrica do Projeto — ML Pipeline com Monitoramento

---

## 1. Data Ingestion

| Critério | Requisitos |
|---|---|
| Atualizar dados de treinamento para re-treinamento | Ver detalhes abaixo |

**Requisitos do script `ingestion.py`:**

- Ler todos os arquivos contidos na pasta `data/` para Python
- Compilar todos os arquivos em um DataFrame pandas e salvar como `finaldata.csv` (com deduplicação antes de salvar)
- Registrar os arquivos ingeridos em `ingestedfiles.txt`

---

## 2. Training, Scoring e Deployment

| Critério | Requisitos |
|---|---|
| Treinar e salvar um modelo de ML | `training.py` — modelo salvo no formato pickle |
| Realizar scoring do modelo | `scoring.py` — métrica: F1 score |
| Persistir o score do modelo | `scoring.py` — escrever o F1 score em `latestscore.txt` |
| Re-deployment regular do modelo | `deployment.py` — copiar modelo, F1 score e registro de ingestão para o diretório de produção |

---

## 3. Diagnostics

| Critério | Requisitos |
|---|---|
| Verificar latência de treinamento e predição | `diagnostics.py` — medir tempo (em segundos) para ingestão e treinamento |
| Verificar integridade e estabilidade dos dados | `diagnostics.py` — medir % de valores NA por coluna numérica |
| Verificar dependências dos scripts | `diagnostics.py` — comparar versão instalada vs. versão mais recente de cada módulo em `requirements.txt` |

**Funções adicionais em `diagnostics.py`:**

- Estatísticas descritivas (média, mediana e moda) para cada coluna numérica
- Função para realizar predições a partir do modelo em produção e um dataset de entrada

---

## 4. Reporting

| Critério | Requisitos |
|---|---|
| Criar APIs para acesso automatizado aos resultados | `app.py` — ver endpoints abaixo |
| Gerar relatório com matriz de confusão | `reporting.py` — matriz de confusão no dataset de teste (`/testdata/`) |
| Combinar outputs das APIs em relatório | `apicalls.py` — salvar outputs combinados em `apireturns.txt` |

**Endpoints obrigatórios em `app.py`:**

- **Scoring** — score do modelo sobre dados de teste (`/testdata/`)
- **Summary statistics** — estatísticas descritivas dos dados ingeridos (diretório `output_folder_path` em `config.json`)
- **Diagnostics** — timing, verificação de dependências e dados faltantes (diretório `output_folder_path`)
- **Predictions** — predições do modelo em produção (`prod_deployment_path`) para um dataset passado como input

---

## 5. Process Automation

| Critério | Requisitos |
|---|---|
| Determinar se o modelo precisa ser atualizado | `fullprocess.py` — checar novos dados e model drift |
| Re-deployment regular em produção | `deployment.py` + cron job executando `fullprocess.py` |

**Lógica de `fullprocess.py`:**

1. Verificar se existem dados não ingeridos em `/sourcedata/`
2. Verificar se o modelo mais recente supera o modelo atualmente em produção (model drift)
3. Chamar `deployment.py` **somente se** ambas as condições forem verdadeiras: novos dados ingeridos **E** model drift detectado

**Configuração do cron job:** agendar a execução periódica de `fullprocess.py`

---

## Sugestões para Destacar o Projeto

- Gerar relatórios em PDF contendo gráficos, diagnósticos e estatísticas descritivas do modelo
- Armazenar e analisar tendências temporais, incluindo variações de latência e percentual de valores faltantes
- Substituir arquivos `.csv` e `.txt` por bancos de dados SQL para armazenamento de datasets e registros