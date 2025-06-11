import hashlib
import re
from datetime import datetime
import boto3
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# === CONFIGURAÇÕES ===
REGION = 'us-east-1'
SERVICE = 'es'
HOST = 'SEU-ENDPOINT.opensearch.amazonaws.com'
BUCKET_NAME = 'compliance-legislacoes'
PREFIX = 'output/'
INDEX_NAME = 'compliance_docs'

# === AUTENTICAÇÃO ===
session = boto3.Session()
credentials = session.get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    REGION,
    SERVICE,
    session_token=credentials.token
)

# === CONEXÃO COM OPENSEARCH ===
client = OpenSearch(
    hosts=[{'host': HOST, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# === MODELO DE EMBEDDING ===
modelo = SentenceTransformer("all-MiniLM-L6-v2")

# === FUNÇÕES AUXILIARES ===
def gerar_hash(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

def extrair_artigo(texto):
    match = re.match(r'(art_\d+[a-zA-Zº]*)', texto)
    return match.group(1).replace('_', ' ') if match else 'artigo desconhecido'

def limpar_texto(texto):
    return re.sub(r'^art_\d+[a-zA-Zº]*_', '', texto)

def atualizar_documento(doc_id, texto, metadados):
    hash_novo = gerar_hash(texto)
    versao_hoje = datetime.today().strftime('%Y-%m-%d')

    try:
        doc_antigo = client.get(index=INDEX_NAME, id=doc_id)
        hash_antigo = doc_antigo['_source'].get('hash')
        if hash_novo == hash_antigo:
            print(f"[OK] Documento '{doc_id}' não sofreu alterações.")
            return
        else:
            print(f"[UPDATE] Documento '{doc_id}' atualizado.")
    except:
        print(f"[NEW] Documento '{doc_id}' será criado.")

    embedding = modelo.encode([texto])[0].tolist()
    doc = {
        "id": doc_id,
        "texto": texto,
        "hash": hash_novo,
        "versao": versao_hoje,
        "ativo": True,
        "embedding": embedding,
        **metadados
    }
    client.index(index=INDEX_NAME, id=doc_id, body=doc)

# === PROCESSA TODOS OS ARQUIVOS XLSX NO BUCKET ===
def processar_arquivos_s3():
    s3 = boto3.client("s3")
    resposta = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)

    for obj in resposta.get("Contents", []):
        key = obj["Key"]
        if not key.endswith(".xlsx"):
            continue

        nome_arquivo = key.split("/")[-1]
        local_tmp = f"/tmp/{nome_arquivo}"

        print(f"[DOWNLOAD] {key}")
        s3.download_file(BUCKET_NAME, key, local_tmp)

        df = pd.read_excel(local_tmp)
        for _, row in df.iterrows():
            titulo = row['Norma']
            descricao = row['Descrição']
            artigo = extrair_artigo(descricao)
            texto_limpo = limpar_texto(descricao)
            doc_id = gerar_hash(titulo + artigo)

            metadados = {
                "tipo": "lei",
                "titulo": titulo,
                "artigo": artigo,
            }

            atualizar_documento(doc_id, texto_limpo, metadados)

# === EXECUTA ===
if __name__ == "__main__":
    processar_arquivos_s3()
