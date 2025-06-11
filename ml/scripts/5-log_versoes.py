
import csv
import json
import os
from datetime import datetime

LOG_CSV = "log_versoes.csv"
LOG_JSON = "log_versoes.json"

def registrar_log(doc_id, titulo, artigo, hash_novo, acao):
    data = {
        "timestamp": datetime.now().isoformat(),
        "id": doc_id,
        "titulo": titulo,
        "artigo": artigo,
        "hash": hash_novo,
        "acao": acao
    }

    # CSV
    existe_csv = os.path.isfile(LOG_CSV)
    with open(LOG_CSV, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if not existe_csv:
            writer.writeheader()
        writer.writerow(data)

    # JSON (append a lista de logs)
    logs = []
    if os.path.isfile(LOG_JSON):
        with open(LOG_JSON, 'r', encoding='utf-8') as f:
            try:
                logs = json.load(f)
            except Exception:
                logs = []

    logs.append(data)
    with open(LOG_JSON, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

# Exemplo de uso
if __name__ == "__main__":
    registrar_log("abc123", "Lei nº 123/2023", "art_1o", "HASH123XYZ", "criado")
