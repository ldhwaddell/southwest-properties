import importlib
import json

from typing import Dict

from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


class TransformOperator(BaseOperator):
    def __init__(
        self,
        raw_data_table,
        transform_fn_name,
        transform_fn_file,
        pg_conn_id,
        *args,
        **kwargs,
    ):
        super(TransformOperator, self).__init__(*args, **kwargs)
        self.raw_data_table = raw_data_table
        self.transform_fn_name = transform_fn_name
        self.transform_fn_file = transform_fn_file
        self.pg_conn_id = pg_conn_id

    def execute(self, context):
        transform_function = getattr(
            importlib.import_module(self.transform_fn_file), self.transform_fn_name
        )

        # Fetch most recent record
        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)
        sql = f"SELECT * FROM {self.raw_data_table} ORDER BY created_at DESC LIMIT 1"
        record = pg_hook.get_first(sql)

        # Check if record is not empty
        if not record:
            raise ValueError(f"No data found in {self.raw_data_table}")

        result = transform_function(record)
