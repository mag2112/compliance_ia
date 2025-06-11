# DAG de exemplo para orquestrar com Airflow
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess

# Define argumentos default do DAG
default_args = {
    'owner': 'compliance-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Função para executar scripts externos
def run_script(script_path):
    subprocess.run(['python3', script_path], check=True)

with DAG(
    dag_id='pipeline_compliance_semantica',
    default_args=default_args,
    description='Pipeline de ingestao e busca semantica para documentos legais',
    schedule_interval='@daily',
    catchup=False,
    tags=['compliance', 'semantic', 'opensarch']
) as dag:

    criar_indice = PythonOperator(
        task_id='criar_indice_opensearch',
        python_callable=run_script,
        op_args=['/opt/airflow/scripts/criar_indice.py']
    )

    processar_documentos = PythonOperator(
        task_id='processar_documentos_s3',
        python_callable=run_script,
        op_args=['/opt/airflow/scripts/processar_arquivos.py']
    )

    consulta_semantica = PythonOperator(
        task_id='executar_consulta_semantica',
        python_callable=run_script,
        op_args=['/opt/airflow/scripts/consulta_semantica.py']
    )

    criar_indice >> processar_documentos >> consulta_semantica
