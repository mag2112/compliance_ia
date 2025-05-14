import os
import time
import re
import unicodedata
import pandas as pd
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# === Baixar Excel do S3 ===
s3 = boto3.client("s3")
bucket_name = "compliance-legislacoes"
s3_key = "entrada/Legislacoes_Artigos_Processados.xlsx"
local_path = "Legislacoes_Artigos_Processados.xlsx"

print(f"⬇️ Baixando planilha de s3://{bucket_name}/{s3_key}")
s3.download_file(bucket_name, s3_key, local_path)
print("✅ Planilha baixada com sucesso")

# === Função para normalizar texto ===
def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    texto = re.sub(r'[.•·]{2,}', ' ', texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.lower()
    texto = re.sub(r'[^a-z0-9\s\.]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# === Configuração do Selenium (usando Chrome headless no container) ===
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)

# === Ler o Excel baixado ===
df = pd.read_excel(local_path, sheet_name="Sistema Antigo")

# === Processamento das leis ===
todos_artigos = []

for index, row in df.iterrows():
    url = row['Link']
    fonte_nome = row['Norma']
    tema_nome = row['Categoria']

    print(f"🔍 Acessando: {url}")
    try:
        driver.get(url)
        time.sleep(5)

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        raw_text = soup.get_text(separator='\n')

        padrao = re.compile(r'(Art\.\s*\d+[º°\w]*.*?)((?=Art\.\s*\d+[º°\w]*)|$)', re.DOTALL)
        matches = padrao.findall(raw_text)

        for match in matches:
            artigo_completo = match[0].strip()
            artigo_id_match = re.search(r'Art\.\s*\d+[º°\w]*', artigo_completo)
            artigo_id = artigo_id_match.group(0) if artigo_id_match else ""

            todos_artigos.append({
                "Categoria": tema_nome,
                "Norma": fonte_nome,
                "Descrição": normalizar(artigo_completo)
            })
    except Exception as e:
        print(f"❌ Erro ao processar {url}: {e}")

driver.quit()

# === Salvar o resultado ===
output_file = "Legislacoes_Artigos_Processados.xlsx"
df_artigos = pd.DataFrame(todos_artigos)
df_artigos.to_excel(output_file, index=False)
print(f"📄 Arquivo gerado: {output_file}")

# === Enviar para o S3 ===
s3_output_key = f"output/{output_file}"
s3.upload_file(output_file, bucket_name, s3_output_key)
print(f"✅ Arquivo enviado para s3://{bucket_name}/{s3_output_key}")
