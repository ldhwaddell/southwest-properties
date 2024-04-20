import json
import logging

from typing import Dict

from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import psycopg2

from modules.utils import load_from_redis

# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


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

        # Create dict for easier lookups
        id_dict: Dict[str, Dict] = {item["id"]: item for item in value}

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

            cursor.executemany(insert_query, [(id,) for id in id_dict.keys()])

            # Find scraped rows that are NOT active
            not_active_query = """
                SELECT s.id
                FROM scraped_ids s
                LEFT JOIN active_applications a ON s.id = a.id
                WHERE a.id IS NULL;
            """
            # Insert the the rows
            cursor.execute(not_active_query)
            not_active_records = cursor.fetchall()

            if not not_active_records:
                logging.info("No new records to insert")
            else:
                logging.info(f"Inserting {len(not_active_records)} new records")
                for (id,) in not_active_records:
                    # Get the corresponding scraped record
                    record = id_dict[id]

                    # Build the query
                    cols = ", ".join(record.keys())
                    placeholders = ", ".join(["%s"] * len(record))
                    updates = ", ".join(
                        [f"{col} = EXCLUDED.{col}" for col in record.keys()]
                    )
                    upsert_application_query = (
                        f"INSERT INTO applications ({cols}) VALUES ({placeholders}) "
                        f"ON CONFLICT (id) DO UPDATE SET {updates};"
                    )

                    # Insert the applications
                    cursor.execute(upsert_application_query, tuple(record.values()))

                    # Insert the active ID
                    upsert_id_query = """
                        INSERT INTO active_applications (id) VALUES (%s) 
                        ON CONFLICT (id) DO NOTHING;
                    """
                    cursor.execute(upsert_id_query, (id,))

            # # Find scraped rows that are already active
            # already_active_query = """
            #     SELECT s.id
            #     FROM scraped_ids s
            #     INNER JOIN active_applications a ON s.id = a.id;
            # """
            # cursor.execute(already_active_query)
            # already_active_records = cursor.fetchall()
            # # Check for changes here
            # print(already_active_records)

            # Find scraped active IDs that are NOT in scraped ids (meaning they are now inactive)
            non_active_query = """
                SELECT a.id
                FROM active_applications a
                LEFT JOIN scraped_ids s ON a.id = s.id
                WHERE s.id IS NULL;
            """
            cursor.execute(non_active_query)
            non_active_ids = cursor.fetchall()

            if not non_active_ids:
                logging.info(f"No records to archive")
            else:
                logging.info(f"Archiving {len(non_active_ids)} records")
                for (id,) in non_active_ids:
                    # Delete from active applications
                    delete_query = "DELETE FROM active_applications WHERE id = %s;"
                    cursor.execute(delete_query, (id,))

                    # Upsert into archived applications
                    insert_archive_query = """
                        INSERT INTO archived_applications (id) VALUES (%s)
                        ON CONFLICT (id) DO UPDATE SET
                        archived_at = CURRENT_TIMESTAMP;
                        """
                    cursor.execute(insert_archive_query, (id,))

            conn.commit()

        except psycopg2.DatabaseError as e:
            conn.rollback()
            logging.error(f"A database error occcurred: {e}")
            raise

        except Exception as e:
            conn.rollback()
            logging.error(f"An unknown error occcurred: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
