from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime
import os

PROJECT_ROOT = os.getenv("AIRFLOW_HOME", os.getcwd())
PYTHON_PATH = f"{PROJECT_ROOT}/.venv/bin/python"
DBT_PATH = f"{PROJECT_ROOT}/electric_vehicles"

with DAG(
    dag_id="electric_vehicles_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@once",
    catchup=True,
    is_paused_upon_creation=False,
) as dag:
    extract_task = BashOperator(
        task_id="extract_data",
        bash_command=f"{PYTHON_PATH} $AIRFLOW_HOME/src/extract/extract.py",
    )

    load_task = BashOperator(
        task_id="load_data",
        bash_command=f"{PYTHON_PATH} $AIRFLOW_HOME/src/load/load.py",
    )

    dbt_transform = BashOperator(
        task_id="dbt_transform",
        bash_command="dbt run",
        cwd=DBT_PATH,
    )

    extract_task >> load_task >> dbt_transform
