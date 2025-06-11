import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from opensearchpy.exceptions import AuthorizationException, TransportError

# Nome do índice
INDEX_NAME = 'compliance_docs'
region = 'us-east-2'

# Credenciais da EC2 (assumindo IAM Role)
session = boto3.Session()
credentials = session.get_credentials().get_frozen_credentials()

awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    'es',
    session_token=credentials.token
)

# Endpoint do OpenSearch
host = 'vpc-compliance-opensearch-6pwgiyup25lkp32dorw4hq2n34.us-east-2.es.amazonaws.com'

# Cliente OpenSearch
client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=30
)

# Mapeamento com 'id' e 'hash'
index_body = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "hash": {"type": "keyword"},
            "titulo": {"type": "text"},
            "texto": {"type": "text"},
            "fonte": {"type": "keyword"},
            "data_documento": {"type": "date"}
        }
    }
}

# Criação condicional
try:
    if not client.indices.exists(INDEX_NAME):
        response = client.indices.create(index=INDEX_NAME, body=index_body)
        print(f"✅ Índice criado: {response}")
    else:
        print(f"ℹ️ Índice '{INDEX_NAME}' já existe.")
except AuthorizationException as ae:
    print("🚫 Erro de autorização (403): verifique se a IAM Role foi mapeada corretamente.")
    print(ae)
except TransportError as te:
    print("⚠️ Erro de transporte:", te)
except Exception as e:
    print("❌ Erro inesperado:", e)
