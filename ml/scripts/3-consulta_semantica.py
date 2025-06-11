import boto3
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection
from sentence_transformers import SentenceTransformer

# === CONFIGURAÇÕES ===
region = 'us-east-1'
service = 'es'
host = 'SEU-ENDPOINT.opensearch.amazonaws.com'  # Substitua pelo seu endpoint
INDEX_NAME = "compliance_docs"

# === AUTENTICAÇÃO IAM ===
session = boto3.Session()
credentials = session.get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

# === CONEXÃO COM OPENSEARCH ===
client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# === CONSULTA ===
consulta_texto = "diretrizes de combate à corrupção no setor público"
modelo = SentenceTransformer("all-MiniLM-L6-v2")
vetor_consulta = modelo.encode([consulta_texto])[0]

query = {
    "size": 3,
    "query": {
        "knn": {
            "embedding": {
                "vector": vetor_consulta.tolist(),
                "k": 3
            }
        }
    }
}

response = client.search(index=INDEX_NAME, body=query)

print(f"Consulta: {consulta_texto}\n")
for i, hit in enumerate(response["hits"]["hits"], 1):
    fonte = hit["_source"].get("titulo", "")
    texto = hit["_source"]["texto"]
    print(f"[{i}] {fonte}:
{texto}\n")
