import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import dataclasses
import datetime as dt
from dateutil.parser import parse
from jinja2 import Template
import logging

import typing as t

import requests

from airflow.decorators import task
from airflow.models import Variable

from utils.clickhouse import clickhouse_conn


@dataclasses.dataclass
class FetchObject:
    record_timestamp: dt.datetime
    record_value: str
    links: t.Dict
    link: str


@task(multiple_outputs=True)
def fetch_events(url: str = "https://api.github.com/events") -> t.Dict:
    """
    curl -L \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/events
    """

    GH_API_TOKEN = Variable.get("gh_api_key")

    headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": GH_API_TOKEN,
            "X-GitHub-Api-Version": "2022-11-28"
        }
    response = requests.get(url,
                            # headers=headers
                            )
    response.raise_for_status()

    return {
            "record_timestamp": dt.datetime.now(),
            "record_value": json.dumps(response.json()),
            "links": response.links,
            "link": response.url
        }


@task
def prepare_range_links(fetch_object: FetchObject) -> t.List[str]:
    obj = FetchObject(**fetch_object)

    url_template = Template("https://api.github.com/events?per_page=30&page={{page_number}}")

    next_url = obj.links.get("next").get("url")
    next_page_number = int(next_url.split("page=")[-1])

    last_url = obj.links.get("last").get("url")
    last_page_number = int(last_url.split("page=")[-1])

    logging.info(f"next_page_number: {next_page_number}, last_page_number: {last_page_number}")

    output_links = [obj.link] + [url_template.render(page_number=n) for n in
                                     range(next_page_number, last_page_number + 1)]

    return output_links


@task
def insert_into_db(fetch_object: FetchObject) -> None:
    obj = FetchObject(**fetch_object)

    logging.info(f"🪣 Inserted obj: {obj.link}")

    client = clickhouse_conn("ch_db_local")
    client.execute("""INSERT INTO raw.github_events_raw(record_timestamp, record_value, link) VALUES""", [obj.__dict__])
    logging.info(f"✅ Successfully inserted obj: {obj.link}")
