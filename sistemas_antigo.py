import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import unicodedata
import boto3
import os

# === Configurações do S3 ===
bucket_name = "compliance-legislacoes"
s3_input_key = "entrada/Legislacoes_Artigos.xlsx"
arquivo_excel = "Legislacoes_Artigos.xlsx"

# === Baixar o Excel do S3 ===
s3 = boto3.client("s3")
print(f"⬇️ Baixando planilha de s3://{bucket_name}/{s3_input_key}")
s3.download_file(bucket_name, s3_input_key, arquivo_excel)

# === Função para normalizar texto (para salvar arquivo) ===
def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    texto = re.sub(r'[.•·]{2,}', ' ', texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.lower()
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    texto = re.sub(r'\s+', '_', texto).strip()
    return texto

# === Configuração do Selenium ===
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)

# === Ler Excel ===
print("📄 Lendo a aba 'Sistema Antigo'")
df = pd.read_excel(arquivo_excel, sheet_name="Sistema Antigo")

# === Processar cada linha individualmente ===
for index, row in df.iterrows():
    url = row['Link']
    fonte_nome = row['Norma']
    tema_nome = row['Categoria']
    artigos = []

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

            artigos.append({
                "Categoria": tema_nome,
                "Norma": fonte_nome,
                "Descrição": normalizar(artigo_completo),
            })

        # === Salvar Excel para essa linha ===
        df_artigos = pd.DataFrame(artigos)
        nome_base = normalizar(fonte_nome)
        output_file = f"{nome_base}.xlsx"
        output_key = f"output/{output_file}"

        df_artigos.to_excel(output_file, index=False)
        print(f"📄 Gerado: {output_file}")

        # === Enviar para o S3 ===
        print(f"⬆️ Enviando para s3://{bucket_name}/{output_key}")
        s3.upload_file(output_file, bucket_name, output_key)
        print(f"✅ Upload concluído: {output_key}")

        os.remove(output_file)  # Remove o arquivo local para economizar espaço

    except Exception as e:
        print(f"❌ Erro ao processar {url}: {e}")

driver.quit()
