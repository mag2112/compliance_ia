import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from opensearchpy.exceptions import AuthorizationException, TransportError

# === Configurações gerais ===
INDEX_NAME = 'compliance_docs'
REGION = 'us-east-2'
HOST = 'vpc-compliance-opensearch-6pwgiyup25lkp32dorw4hq2n34.us-east-2.es.amazonaws.com'

def lambda_handler(event, context):
    try:
        # Obter credenciais da Role da Lambda
        session = boto3.Session()
        credentials = session.get_credentials().get_frozen_credentials()
        
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            REGION,
            'es',
            session_token=credentials.token
        )

        # Criar cliente OpenSearch
        client = OpenSearch(
            hosts=[{'host': HOST, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30
        )

        # Corpo do mapeamento do índice
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

        # Verificar existência do índice e criar se necessário
        if not client.indices.exists(INDEX_NAME):
            response = client.indices.create(index=INDEX_NAME, body=index_body)
            return {
                "statusCode": 200,
                "body": f"✅ Índice criado com sucesso: {response}"
            }
        else:
            return {
                "statusCode": 200,
                "body": f"ℹ️ O índice '{INDEX_NAME}' já existe."
            }

    except AuthorizationException as ae:
        return {
            "statusCode": 403,
            "body": f"🚫 Erro de autorização (403): {str(ae)}"
        }
    except TransportError as te:
        return {
            "statusCode": 502,
            "body": f"⚠️ Erro de transporte OpenSearch: {str(te)}"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"❌ Erro inesperado: {str(e)}"
        }
