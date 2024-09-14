import yaml


def read_yaml(path_to_file: str):
    with open(path_to_file, "r") as f_yaml:
        try:
            content = yaml.safe_load(f_yaml)
            return content
        except yaml.YAMLError as e:
            print(e)