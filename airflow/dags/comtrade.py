from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator

def print_hello():
    return 'Hello world!'

dag = DAG('comtrade', description='Simple tutorial DAG',
          schedule_interval='24 19 * * *',
          start_date=datetime(2017, 3, 20), catchup=False)

dummy_operator = DummyOperator(task_id='dummy_task', retries=3, dag=dag)



hello_operator = PythonOperator(task_id='hello_task', python_callable=print_hello, dag=dag)

bash_operator = BashOperator(
    task_id='also_run_this',
    bash_command='python3 /home/scraper/AIS/main.py',
)

dummy_operator >> hello_operator
hello_operator >> bash_operator