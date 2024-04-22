from datetime import datetime
import json
import logging
import pendulum

from typing import Dict

from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import psycopg2
import psycopg2.extras

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
        active_table,
        archive_table,
        history_table,
        table,
        *args,
        **kwargs,
    ):
        super(LoadOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = pg_conn_id
        self.redis_conn_id = redis_conn_id
        self.redis_key = redis_key
        self.pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)
        self.conn = self.pg_hook.get_conn()
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.active_table = active_table
        self.table = table
        self.archive_table = archive_table
        self.history_table = history_table

    def archive(self):
        """
        Query for scraped active IDs that are NOT in scraped ids (meaning they are now inactive).
        Archives these records
        """

        non_active_query = f"""
            SELECT a.id
            FROM {self.active_table} a
            LEFT JOIN scraped_ids s ON a.id = s.id
            WHERE s.id IS NULL;
        """
        self.cursor.execute(non_active_query)
        non_active_ids = self.cursor.fetchall()

        if not non_active_ids:
            logging.info(f"No records to archive")
        else:
            logging.info(f"Archiving {len(non_active_ids)} records")
            for non_active_id in non_active_ids:
                id = non_active_id["id"]

                # Delete from active records
                delete_query = f"DELETE FROM {self.active_table} WHERE id = %s;"
                self.cursor.execute(delete_query, (id,))

                # Upsert into archived records
                insert_archive_query = f"""
                    INSERT INTO {self.archive_table} (id) VALUES (%s)
                    ON CONFLICT (id) DO UPDATE SET
                    archived_at = CURRENT_TIMESTAMP;
                    """
                self.cursor.execute(insert_archive_query, (id,))

    def add_new(self, id_dict: Dict):
        """
        Finds scraped rows that are not already active. These are new records.
        Upsert them into the main table and add their ID to the active table
        """

        not_active_query = f"""
            SELECT s.id
            FROM scraped_ids s
            LEFT JOIN {self.active_table} a ON s.id = a.id
            WHERE a.id IS NULL;
        """
        # Insert the the rows
        self.cursor.execute(not_active_query)
        not_active_records = self.cursor.fetchall()

        if not not_active_records:
            logging.info("No new records to insert")
        else:
            logging.info(f"Inserting {len(not_active_records)} new records")
            for not_active_record in not_active_records:
                id = not_active_record["id"]

                # Get the corresponding scraped record
                record: Dict = id_dict[id]

                # Build the query
                cols = ", ".join(record.keys())
                placeholders = ", ".join(["%s"] * len(record))
                updates = ", ".join(
                    [f"{col} = EXCLUDED.{col}" for col in record.keys()]
                )

                upsert_record_query = f"""
                    INSERT INTO {self.table} ({cols}) VALUES ({placeholders}) 
                    ON CONFLICT (id) DO UPDATE SET {updates};
                """

                record_values = [
                    json.dumps(value) if isinstance(value, (dict, list)) else value
                    for value in record.values()
                ]

                # Insert the new records
                self.cursor.execute(upsert_record_query, tuple(record_values))

                # Insert the active ID
                upsert_id_query = f"""
                    INSERT INTO {self.active_table} (id) VALUES (%s) 
                    ON CONFLICT (id) DO NOTHING;
                """
                self.cursor.execute(upsert_id_query, (id,))

    def update_existing(self, id_dict: Dict):
        """
        Find scraped rows that are already active and check for changes. Save changes to histories table.
        Updates records to reflect most recent changes
        """

        already_active_query = f"""
            SELECT s.id
            FROM scraped_ids s
            INNER JOIN {self.active_table} a ON s.id = a.id;
        """
        self.cursor.execute(already_active_query)
        already_active_records = self.cursor.fetchall()

        if not already_active_records:
            logging.info("No existing records to check for changes")
        else:
            logging.info(
                f"Found {len(already_active_records)} existing records. Checking for changes"
            )
            for active_record in already_active_records:
                id = active_record["id"]

                # Get the corresponding scraped record
                scraped_record = id_dict[id]

                existing_record_query = f"SELECT * FROM {self.table} WHERE id = %s"

                self.cursor.execute(existing_record_query, (id,))
                existing_record = self.cursor.fetchone()

                updates = {}
                ignore_fields = set()
                for key in scraped_record:
                    if key in ignore_fields or key not in existing_record:
                        continue

                    existing_value = None
                    scraped_value = None

                    if isinstance(existing_record[key], datetime):
                        if pendulum.parse(scraped_record[key]) != existing_record[key]:
                            updates[key] = scraped_record[key]
                            existing_value = existing_record[key]
                            scraped_value = scraped_record[key]

                    elif isinstance(existing_record[key], (list, dict)):
                        if existing_record[key] != scraped_record[key]:
                            updates[key] = json.dumps(scraped_record[key])
                            existing_value = json.dumps(existing_record[key])
                            scraped_value = json.dumps(scraped_record[key])

                    else:
                        if scraped_record[key] != existing_record[key]:
                            updates[key] = scraped_record[key]
                            existing_value = existing_record[key]
                            scraped_value = scraped_record[key]

                    if existing_value and scraped_value:
                        # Record history of changes
                        insert_history_query = f"INSERT INTO {self.history_table} (existing_record_id, changed, original, updated) VALUES (%s, %s, %s, %s)"
                        self.cursor.execute(
                            insert_history_query,
                            (id, key, existing_value, scraped_value),
                        )

                # Perform update if any changes found
                if updates:
                    logging.info(f"{len(updates)} change(s) found for record {id}")
                    update_parts = ", ".join([f"{key} = %s" for key in updates.keys()])
                    update_values = list(updates.values()) + [id]
                    upsert_existing_record_query = (
                        f"UPDATE {self.table} SET {update_parts} WHERE id = %s;"
                    )
                    self.cursor.execute(upsert_existing_record_query, update_values)

    def execute(self, context):
        value = load_from_redis(conn_id=self.redis_conn_id, key=self.redis_key)
        value: Dict = json.loads(value)

        # Create dict for easier lookups
        id_dict = {item["id"]: item for item in value}

        try:
            self.cursor.execute(
                """
                CREATE TEMPORARY TABLE scraped_ids (
                    id VARCHAR(64) PRIMARY KEY
                ) ON COMMIT DROP;
            """
            )
            insert_query = "INSERT INTO scraped_ids (id) VALUES (%s);"

            self.cursor.executemany(insert_query, [(id,) for id in id_dict.keys()])

            self.update_existing(id_dict)
            self.add_new(id_dict)
            self.archive()

            self.conn.commit()

        except psycopg2.DatabaseError as e:
            self.conn.rollback()
            logging.error(f"A database error occcurred: {e}")
            raise

        except Exception as e:
            self.conn.rollback()
            logging.error(f"An unknown error occcurred: {e}")
            raise
        finally:
            self.cursor.close()
            self.conn.close()
