import os
import re
import time
import unicodedata
import pandas as pd
import boto3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import hashlib
from datetime import datetime

# === CONFIGURAÇÕES ===
bucket_name = "compliance-legislacoes"
s3_input_key = "entrada/Legislacoes_Artigos.xlsx"
output_prefix = "output/"
index_name = "compliance_docs"
region = "us-east-2"
host = "vpc-compliance-opensearch-6pwgiyup25lkp32dorw4hq2n34.us-east-2.es.amazonaws.com"

# === DOWNLOAD DA PLANILHA PRINCIPAL ===
def fase_1_coleta_com_selenium():
    print("🕷️ Iniciando fase 1 - Coleta via Selenium")

    s3 = boto3.client("s3")
    local_file = "Legislacoes_Artigos.xlsx"

    print(f"⬇️ Baixando s3://{bucket_name}/{s3_input_key}")
    s3.download_file(bucket_name, s3_input_key, local_file)

    df = pd.read_excel(local_file, sheet_name="Sistema Antigo")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)

    for _, row in df.iterrows():
        url = row['Link']
        norma = row['Norma']
        categoria = row['Categoria']
        artigos = []

        print(f"🌐 Acessando {url}")
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
                artigos.append({
                    "Categoria": categoria,
                    "Norma": norma,
                    "Descrição": normalizar(artigo_completo),
                })

            df_artigos = pd.DataFrame(artigos)
            nome_base = normalizar(norma)
            arquivo_saida = f"{nome_base}.xlsx"
            s3_key_saida = f"{output_prefix}{arquivo_saida}"

            df_artigos.to_excel(arquivo_saida, index=False)
            s3.upload_file(arquivo_saida, bucket_name, s3_key_saida)
            os.remove(arquivo_saida)
            print(f"✅ Enviado: {s3_key_saida}")

        except Exception as e:
            print(f"❌ Erro ao acessar {url}: {e}")

    driver.quit()

# === EMBEDDINGS + INDEXAÇÃO ===
def fase_2_embeddings_e_indexacao():
    print("🧠 Iniciando fase 2 - Geração de embeddings + indexação")

    s3 = boto3.client("s3")
    resposta = s3.list_objects_v2(Bucket=bucket_name, Prefix=output_prefix)
    modelo = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")  # 768 dim

    session = boto3.Session()
    credentials = session.get_credentials().get_frozen_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es', session_token=credentials.token)

    client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    for obj in resposta.get("Contents", []):
        key = obj["Key"]
        if not key.endswith(".xlsx"):
            continue

        print(f"⬇️ Baixando {key}")
        local_tmp = f"/tmp/{key.split('/')[-1]}"
        s3.download_file(bucket_name, key, local_tmp)

        df = pd.read_excel(local_tmp)
        for _, row in df.iterrows():
            titulo = row['Norma']
            descricao = row['Descrição']
            categoria = row['Categoria']
            texto = descricao

            doc_id = gerar_hash(titulo + descricao)
            hash_novo = gerar_hash(texto)

            try:
                doc_antigo = client.get(index=index_name, id=doc_id)
                if doc_antigo['_source'].get('hash') == hash_novo:
                    print(f"[SKIP] Documento {doc_id} já existe.")
                    continue
            except:
                pass

            embedding = modelo.encode([texto])[0].tolist()
            doc = {
                "id": doc_id,
                "titulo": titulo,
                "texto": texto,
                "fonte": "Sistema Antigo",
                "data_documento": datetime.today().strftime('%Y-%m-%d'),
                "hash": hash_novo,
                "categoria": categoria,
                "embedding": embedding
            }

            client.index(index=index_name, id=doc_id, body=doc)
            print(f"[OK] Documento {doc_id} indexado.")

        os.remove(local_tmp)

# === FUNÇÕES AUXILIARES ===
def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    texto = re.sub(r'[.•·]{2,}', ' ', texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto = texto.lower()
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    texto = re.sub(r'\s+', '_', texto).strip()
    return texto

def gerar_hash(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

# === EXECUÇÃO ===
def main():
    print("🚀 Iniciando pipeline completo de compliance")
    fase_1_coleta_com_selenium()
    fase_2_embeddings_e_indexacao()
    print("🏁 Pipeline finalizado com sucesso.")

if __name__ == "__main__":
    main()
