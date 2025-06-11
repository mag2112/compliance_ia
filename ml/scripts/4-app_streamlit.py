
import streamlit as st
from sentence_transformers import SentenceTransformer
import boto3
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection

# Configurações
region = 'us-east-1'
service = 'es'
host = 'SEU-ENDPOINT.opensearch.amazonaws.com'
index_name = 'compliance_docs'

# Autenticação IAM
session = boto3.Session()
credentials = session.get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

# Conexão OpenSearch
client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Carregar modelo
modelo = SentenceTransformer('all-MiniLM-L6-v2')

# Streamlit UI
st.title("🔍 Busca Semântica de Leis e Artigos")
query_text = st.text_input("Digite sua consulta semântica:")

if st.button("Buscar") and query_text:
    vetor = modelo.encode([query_text])[0].tolist()
    query = {
        "size": 5,
        "query": {
            "knn": {
                "embedding": {
                    "vector": vetor,
                    "k": 5
                }
            }
        }
    }

    response = client.search(index=index_name, body=query)

    st.subheader(f"Resultados para: "{query_text}"")
    for i, hit in enumerate(response['hits']['hits'], 1):
        st.markdown(f"### {i}. {hit['_source']['titulo']}")
        st.markdown(f"*Artigo:* `{hit['_source']['artigo']}`")
        st.markdown(hit['_source']['texto'])
        st.markdown("---")
