from airflow import DAG
from airflow.providers.amazon.aws.operators.batch import BatchOperator
from airflow.providers.amazon.aws.sensors.s3_key import S3KeySensor
from airflow.utils.dates import days_ago

with DAG(
    dag_id="etl_legislacoes_batch_dag",
    start_date=days_ago(1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    executar_job = BatchOperator(
        task_id="executar_batch",
        job_name="extrair_legislacoes",
        job_queue="legisla_batch_queue",
        job_definition="legisla_batch_def",
        overrides={"command": ["python", "sistemas_antigo.py"]},
        region_name="us-east-1"
    )

    aguardar_arquivo = S3KeySensor(
        task_id="aguardar_primeira_saida",
        bucket_key="output/leis/lei_anticorrupcao.xlsx",  # exemplo
        bucket_name="compliance-legislacoes",
        poke_interval=60,
        timeout=600
    )

    executar_job >> aguardar_arquivo
