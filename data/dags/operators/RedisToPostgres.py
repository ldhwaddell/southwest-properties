import json

from typing import Dict

from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.redis.hooks.redis import RedisHook


class RedisToPostgresOperator(BaseOperator):
    def __init__(
        self,
        pg_conn_id,
        redis_conn_id,
        redis_key,
        table_name,
        *args,
        **kwargs,
    ):
        super(RedisToPostgresOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = pg_conn_id
        self.redis_conn_id = redis_conn_id
        self.redis_key = redis_key
        self.table_name = table_name

    def execute(self, context):
        redis_hook = RedisHook(redis_conn_id=self.redis_conn_id).get_conn()

        with redis_hook.pipeline() as pipe:
            pipe.get(self.redis_key)
            pipe.delete(self.redis_key)
            result = pipe.execute()

        # [0] is get, [1] is delete status
        value = result[0]

        if value is None:
            raise ValueError(f"No data found in Redis for key: {self.redis_key}")

        value: Dict = json.loads(value)
        cols = ", ".join([str(i) for i in value.keys()])  # column names as a string
        placeholders = ", ".join(["%s"] * len(value))  # placeholders for the values
        values = []

        # Stringify any dicts or lists
        for v in value.values():
            if isinstance(v, (dict, list)):
                v = json.dumps(v)
            values.append(v)

        # Create a tuple of values for SQL
        parameters = tuple(values)

        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)
        insert_query = f"INSERT INTO {self.table_name} ({cols}) VALUES ({placeholders})"

        pg_hook.run(insert_query, parameters=parameters)
