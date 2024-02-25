import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import datetime as dt

from airflow.decorators import dag
from airflow.utils.trigger_rule import TriggerRule
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import get_current_context

from github_events.scripts.tasks import fetch_events, prepare_range_links, insert_into_db

args = {
    "owner": "urevoleg",
    'retries': 5,
    'retry_delay': dt.timedelta(minutes=3),
}


@dag(dag_id="dag_github_events",
     schedule="*/5 * * * *",
     start_date=dt.datetime(2024, 2, 1),
     catchup=False,
     default_args=args)
def create_dag():
    start = EmptyOperator(
        task_id="start",
    )

    end = EmptyOperator(
        task_id="end",
        trigger_rule=TriggerRule.ALL_SUCCESS
    )

    obj = fetch_events()

    prepared_links = prepare_range_links(fetch_object=obj)

    fetch_events_by_url = fetch_events.expand(url=prepared_links)

    insert = insert_into_db.expand(fetch_object=fetch_events_by_url)

    start >> obj >> prepared_links >> fetch_events_by_url >> insert >> end

create_dag()
