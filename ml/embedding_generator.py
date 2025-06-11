from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np

def gerar_embeddings(lista_textos):
    print("[INFO] Carregando modelo de embeddings...")
    modelo = SentenceTransformer("all-MiniLM-L6-v2")
    print("[INFO] Gerando embeddings...")
    embeddings = modelo.encode(lista_textos, show_progress_bar=True)
    return embeddings

if __name__ == "__main__":
    # Exemplo de uso com textos fictícios
    textos = [
        "Política Anticorrupção aprovada em 2023.",
        "Lei de Proteção de Dados regulamenta o uso de dados pessoais."
    ]
    embeddings = gerar_embeddings(textos)
    print("[INFO] Embeddings gerados com shape:", embeddings.shape)
