import datetime as dt

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup


def create_dag(intergation_metadata: dict) -> DAG:

    dag_id = f'dwh_walle_{intergation_metadata["name"]}'
    description = intergation_metadata["description"]
    schedule_interval = intergation_metadata["dag"]["schedule_interval"]
    owner = intergation_metadata["dag"]["owner"]
    start_date = intergation_metadata["dag"]["start_date"]
    end_date = intergation_metadata["dag"].get("end_date", None)
    catchup = intergation_metadata["dag"]["catchup"]
    tags = intergation_metadata["dag"]["tags"]

    default_args = {"owner": owner,
                    "start_date": start_date,
                    "end_date": end_date,
                    "retries": 5,
                    "retry_delay": dt.timedelta(minutes=5), }

    dag = DAG(dag_id,
              description=description,
              schedule_interval=schedule_interval,
              default_args=default_args,
              catchup=catchup,
              tags=["walle"] + tags)

    with (dag):
        with TaskGroup("TaskGroup") as gr:
            start = EmptyOperator(task_id="Start", dag=dag)
            end = EmptyOperator(task_id="End", dag=dag)

            start >> end

    return dag_id, dag