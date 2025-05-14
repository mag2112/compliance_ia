# Projeto Compliance IA 

---

## ☁️ Arquitetura AWS Utilizada

### ✅ **1. Amazon S3**
- **Bucket**: `compliance-legislacoes`
- **Objetivo**: Armazenar a planilha de entrada `Legislacoes_Unificadas_Awake.xlsx` e arquivos de saída gerados pelo script (como `.xlsx`, `.md`).

### ✅ **2. AWS Batch – Compute Environment**
- **Nome**: `compliance-batch-compute`
- **Tipo**: EC2 Spot (baixo custo)
- **vCPUs**: mínimo `0`, máximo `2`
- **Instâncias**: tipo `optimal` (auto-escolha)
- **Orquestração**: Gerenciada (`Managed`)
- **Role**: `BatchInstanceRoleWithS3` com acesso ao S3

### ✅ **3. AWS Batch – Job Queue**
- **Nome**: `compliance-job-queue`
- **Prioridade**: 1
- **Compute Environment**: conectado com `compliance-batch-compute`

---

## ⚙️ Execução do Script

O script `sistemas_antigo.py`:

- Faz leitura da planilha no S3
- Usa Selenium Headless + BeautifulSoup para navegar e extrair os artigos de cada legislação
- Normaliza o conteúdo e salva um Excel com os dados tratados

---

## ⏭️ Próximos Passos

- [ ] Criar imagem Docker com Selenium e o script Python
- [ ] Subir para o Amazon ECR
- [ ] Criar o **Job Definition** no AWS Batch
- [ ] (Opcional) Automatizar via Airflow (MWAA)

---

## 📌 Requisitos da Imagem Docker

A imagem incluirá:

- Python 3.9+
- Selenium com Chrome Headless
- ChromeDriver
- bibliotecas: `boto3`, `pandas`, `beautifulsoup4`, `openpyxl`

---

## 📞 Contato

Dúvidas ou sugestões? Abra uma issue ou envie um pull request.

---

**Marco** – Projeto de Compliance Inteligente com IA, Cloud e Automação.

