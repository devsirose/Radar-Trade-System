from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'retrain_lstm_model',
    default_args=default_args,
    schedule_interval='*/30 * * * *',
    catchup=False
)

retrain = BashOperator(
    task_id='train_model',
    bash_command='python /app/train/train_lstm.py',
    dag=dag
)

