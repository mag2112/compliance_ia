from opensearchpy import OpenSearch
import numpy as np
import json

# Configuração do cliente OpenSearch
client = OpenSearch(
    hosts=[{'host': 'SEU-ENDPOINT-OPENSEARCH', 'port': 443}],
    http_auth=('usuario', 'senha'),
    use_ssl=True,
)

INDEX_NAME = "compliance_docs"

def indexar_vetores(textos, embeddings):
    for i, (texto, vetor) in enumerate(zip(textos, embeddings)):
        doc = {
            "id": i,
            "texto": texto,
            "embedding": vetor.tolist()
        }
        response = client.index(index=INDEX_NAME, id=i, body=json.dumps(doc))
        print(f"[INFO] Documento {i} indexado:", response['result'])

if __name__ == "__main__":
    from embedding_generator import gerar_embeddings

    textos = [
        "Política de Sustentabilidade implementada em 2022.",
        "Relatório de auditoria interna com foco em riscos regulatórios."
    ]
    embeddings = gerar_embeddings(textos)
    indexar_vetores(textos, embeddings)
