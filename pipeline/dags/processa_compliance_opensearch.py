from airflow import DAG
from airflow.providers.amazon.aws.operators.batch import BatchOperator
from datetime import datetime

# === DAG: Executa job do AWS Batch para gerar embeddings e indexar no OpenSearch ===
with DAG(
    dag_id="processa_compliance_opensearch",
    description="Executa diariamente job AWS Batch que processa legislações e indexa no OpenSearch",
    schedule_interval="0 2 * * *",  # 02:00 UTC → 23h BRT
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["compliance", "batch", "opensearch"]
) as dag:

    executar_job_batch = BatchOperator(
        task_id="executar_job_compliance_batch",
        job_name="executar-compliance",
        job_definition="compliance-batch-job",    # nome definido no AWS Batch
        job_queue="compliance-batch-queue",       # nome da fila do Batch
        aws_conn_id="aws_default",                # conexão IAM no Airflow
        region_name="us-east-2",
        wait_for_completion=True,
        max_retries=2,
        retries=1
    )
