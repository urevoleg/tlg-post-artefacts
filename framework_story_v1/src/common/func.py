import datetime as dt

import typing as t

import logging

from airflow import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup

from extractors import *
from savers import *
from transformers import *


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

            # 1 блок формирование объектов (пути к файлам на S3 или урлы для API)
            @task(queue="celery_queue")
            def _extractor(extractor: t.Callable) -> t.List[str]:
                extractor_obj = extractor(
                    intergation_metadata=intergation_metadata
                )

                return [resource.s3_filename for resource in extractor_obj.get_objects()]

            # извлекаем extractor
            extractor_name, extractor_params = list(getattr(intergation_metadata, "extractor").items())[0]

            if not extractor_params:
                extractor_params = {}

            logging.info([extractor_name, extractor_params])
            extractor = globals()[extractor_name]

            # возвращаем список объектов
            ext_resources = _extractor.override(task_id=f"_extractor__{extractor_name}")(
                extractor=extractor)

            # 2 блок Трансформации и Сохранение
            # Управление параллельностью
            max_active_tis_per_dag = getattr(intergation_metadata, "max_active_tis_per_dag", 5)

            @task(max_active_tis_per_dag=max_active_tis_per_dag,
                  queue="celery_queue",
                  # executor_config=PodSizeEnum.
                  )
            def _transform_and_load(ext_resource: str,
                                    saver: t.Callable,
                                    transformer: t.Callable, ):

                saver_obj = saver(intergation_metadata=intergation_metadata)

                transformer_obj = transformer(intergation_metadata=intergation_metadata)
                logging.info(f"transformer: {transformer_obj}")

                # transform
                transformer_resource = transformer_obj.transform(
                    resource=ext_resource
                )

                # save
                # костыль
                if transformer_resource:
                    # если есть что сохранять, например, трансформер может самостоятельно сохранить файлы в некоторых кейсах
                    saver_resource = saver_obj.save(
                        resource=transformer_resource,
                    )

                    return {
                        "transformer_name": transformer_name,
                        "saver_resource": saver_resource,
                    }

            # извлекаем saver
            saver_name, _ = list(getattr(intergation_metadata, "saver").items())[0]

            logging.info(saver_name)
            saver = globals()[saver_name]

            # извлекаем transformers
            for transformer_dict in getattr(intergation_metadata, "transformers", []):
                transformer_name, _ = \
                    [(transformer_name, _) for transformer_name, _ in
                     transformer_dict.items()][-1]

                transformer = globals()[transformer_name]

                transform_and_load = _transform_and_load \
                    .override(task_id=f"_transformer_and_saver__{transformer_name}") \
                    .partial(saver=saver,
                             transformer=transformer) \
                    .expand(resource=ext_resources)
            
            end = EmptyOperator(task_id="End", dag=dag)

            start >> ext_resources
            transform_and_load >> end

    return dag_id, dag