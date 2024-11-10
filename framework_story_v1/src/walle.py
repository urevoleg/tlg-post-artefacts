import os
from pprint import pprint

from common.func import create_dag
from yaml_reader.reader import read_yaml


directories = ["metadata"]

for directory in directories:
    for dir_path, dir_names, file_names in os.walk(directory):
        for file in file_names:
            metadata_file = os.path.join(dir_path, file)

            metadata = read_yaml(metadata_file)

            metadata_model = metadata["models"][0]

            pprint(metadata_model)

            #TODO должен быть блок проверок:
            # 1. Наличие экстратора
            # 2. Наличие хотя бы одного трансформера

            dag_id, dag = create_dag(intergation_metadata=metadata_model)
            globals()[dag_id] = dag