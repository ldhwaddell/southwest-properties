# 'airflow' word is required for the dagbag to parse this file
from dagfactory import load_yaml_dags

load_yaml_dags(globals_dict=globals(), suffix=["dag.yaml"])
