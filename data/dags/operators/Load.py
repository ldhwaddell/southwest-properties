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
        self.pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)
        self.conn = self.pg_hook.get_conn()
        self.cursor = self.conn.cursor()

    def archive(self):
        """Query for scraped active IDs that are NOT in scraped ids (meaning they are now inactive). Archives these records"""

        non_active_query = """
            SELECT a.id
            FROM active_applications a
            LEFT JOIN scraped_ids s ON a.id = s.id
            WHERE s.id IS NULL;
        """
        self.cursor.execute(non_active_query)
        non_active_ids = self.cursor.fetchall()

        if not non_active_ids:
            logging.info(f"No records to archive")
        else:
            logging.info(f"Archiving {len(non_active_ids)} records")
            for (id,) in non_active_ids:
                # Delete from active applications
                delete_query = "DELETE FROM active_applications WHERE id = %s;"
                self.cursor.execute(delete_query, (id,))

                # Upsert into archived applications
                insert_archive_query = """
                    INSERT INTO archived_applications (id) VALUES (%s)
                    ON CONFLICT (id) DO UPDATE SET
                    archived_at = CURRENT_TIMESTAMP;
                    """
                self.cursor.execute(insert_archive_query, (id,))

    def add_new(self, id_dict: Dict):
        """
        Finds scrpaed rows that are not already active. These are new records.
        Upsert them into the appplications table and add their ID to the active applications table
        """

        not_active_query = """
            SELECT s.id
            FROM scraped_ids s
            LEFT JOIN active_applications a ON s.id = a.id
            WHERE a.id IS NULL;
        """
        # Insert the the rows
        self.cursor.execute(not_active_query)
        not_active_records = self.cursor.fetchall()

        if not not_active_records:
            logging.info("No new records to insert")
        else:
            logging.info(f"Inserting {len(not_active_records)} new records")
            for (id,) in not_active_records:
                # Get the corresponding scraped record
                record: Dict = id_dict[id]

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
                self.cursor.execute(upsert_application_query, tuple(record.values()))

                # Insert the active ID
                upsert_id_query = """
                    INSERT INTO active_applications (id) VALUES (%s) 
                    ON CONFLICT (id) DO NOTHING;
                """
                self.cursor.execute(upsert_id_query, (id,))

    def update_existing(self, id_dict: Dict):
        """Find scraped rows that are already active and check for changes. Save changes to histories table"""

        already_active_query = """
            SELECT s.id
            FROM scraped_ids s
            INNER JOIN active_applications a ON s.id = a.id;
        """
        self.cursor.execute(already_active_query)
        already_active_records = self.cursor.fetchall()

        if not already_active_records:
            logging.info("No existing records to check for changes")
        else:
            logging.info(
                f"Found {len(already_active_records)} existing records. Checking for changes"
            )
            for (id,) in already_active_records:
                # Get the corresponding scraped record
                record = id_dict[id]

                existing_record_query = "SELECT * FROM applications WHERE id = %s"

                self.cursor.execute(existing_record_query, (id,))
                existing_record = self.cursor.fetchone()

                ...

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

            self.add_new(id_dict)
            self.update_existing(id_dict)
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
