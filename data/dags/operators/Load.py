import json

from typing import Dict

from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from modules.utils import load_from_redis


class LoadOperator(BaseOperator):
    def __init__(
        self,
        pg_conn_id,
        redis_conn_id,
        redis_key,
        *args,
        **kwargs,
    ):
        super(LoadOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = pg_conn_id
        self.redis_conn_id = redis_conn_id
        self.redis_key = redis_key

    def execute(self, context):
        value = load_from_redis(conn_id=self.redis_conn_id, key=self.redis_key)
        value: Dict = json.loads(value)

        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                CREATE TEMPORARY TABLE scraped_ids (
                    id VARCHAR(64) PRIMARY KEY
                ) ON COMMIT DROP;
            """
            )
            insert_query = "INSERT INTO scraped_ids (id) VALUES (%s);"

            # Use executemany to insert all records in one command
            cursor.executemany(insert_query, [(record["id"],) for record in value])

            # Find scraped rows that are already active
            already_active_query = """
                SELECT s.id
                FROM scraped_ids s
                INNER JOIN active_applications a ON s.id = a.id;
            """
            cursor.execute(already_active_query)
            already_active_records = cursor.fetchall()
            print(already_active_records)

            conn.commit()

        except Exception as e:
            conn.rollback()
            print("An error occurred while executing SQL commands:", e)
            raise
        finally:
            cursor.close()
            conn.close()
