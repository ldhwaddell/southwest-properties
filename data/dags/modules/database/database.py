import logging
import os
from typing import List, Dict, Set

from sqlalchemy import create_engine, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import insert

# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


class Database:
    def __init__(self):
        db_url = os.environ.get("AIRFLOW__DATABASE__SQL_ALCHEMY_CONN")
        self.engine = create_engine(db_url)
        self.session_maker = sessionmaker(bind=self.engine)
        self.session: Session = self.session_maker()

    def select_all(self, table):
        """Selects all records from a table"""
        try:
            stmt = select(table)
            results = self.session.execute(stmt)
            return results.scalars()

        except SQLAlchemyError as e:
            logging.error(f"An error occurred while fetching all tables: {e}")
            raise

    def upsert(self, table, data: List[Dict]):
        """
        Upserts data into the desired table table. Cannot do traditional insert as idempotency is
        required if task retries
        """

        logging.info(f"Received {len(data)} items to upsert")

        try:

            for d in data:
                # Use the table object for the insert statement
                insert_stmt = insert(table).values(**d)

                do_update_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=["id"],
                    # Update everything but ID
                    set_={k: d[k] for k in d if k != "id"},
                )

                # Execute the upsert statement
                self.session.execute(do_update_stmt)

            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"An error occurred during {table} upsertion: {e}")
            raise

    def get(self, table, column, condition):
        """Gets records that match a desired condition"""
        try:
            stmt = select(table).where(column == condition)
            result = self.session.execute(stmt)

            return result.scalars()

        except SQLAlchemyError as e:
            logging.error(
                f"An error occurred while getting records from {table.__tablename__} on column {column} with condition {condition}: {e}"
            )
            raise

    def archive(self, table, column, ids: Set[str]):
        """Sets active to false for all the passed record ids"""
        try:
            # Ensure there are IDs to process
            if ids:
                values_to_update = {column: False}

                stmt = update(table).where(table.id.in_(ids)).values(values_to_update)

                result = self.session.execute(stmt)
                self.session.commit()

                logging.info(f"Successfully archived {result.rowcount} records")
            else:
                logging.info("No records to archive")

        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"An error occurred while archiving applications: {e}")
            raise

    def compare_record(
        self, existing_records_table, scraped_record: Dict
    ) -> List[Dict]:
        """Compares an existing record to the scraped one. Records any differences"""
        try:
            # Existing entry
            stmt = select(existing_records_table).where(
                existing_records_table.id == scraped_record["id"]
            )
            existing_record = self.session.execute(stmt).scalar_one_or_none()

            change_records: List[Dict] = []

            # Compare existing entry to keys from scraped application
            for key, value in scraped_record.items():

                # Skip created_at as it will always be different
                if key == "created_at":
                    continue

                # Check if the attribute exists and has a different value
                if (
                    hasattr(existing_record, key)
                    and getattr(existing_record, key) != value
                ):

                    change_record = {
                        "application_id": existing_record.id,
                        "changed": key,
                        "original": str(getattr(existing_record, key)),
                        "updated": str(value),
                    }

                    change_records.append(change_record)

            logging.info(f"{len(change_records)} changes found in {existing_record.id}")

            return change_records
        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"An error occurred while comparing applications: {e}")
            raise

    def update_records(
        self,
        insert_table,
        changes_table,
        archive_field,
        scraped_records,
        existing_records,
    ):
        """Updates the database based on scraped listings."""
        try:
            existing_records_ids = set(record.id for record in existing_records)

            records_to_upsert = []
            changed_records = []
            count = 0

            for record in scraped_records:
                count += 1

                record_data = {
                    key: value
                    for key, value in record.__dict__.items()
                    if not key.startswith("_")
                }

                if record.id in existing_records_ids:
                    # Removing it from existings ids means those left in existing ids are inactive
                    existing_records_ids.remove(record.id)
                    # Check for changes
                    changes = self.compare_record(insert_table, record_data)
                    if changes:
                        changed_records.extend(changes)

                records_to_upsert.append(record_data)

            logging.info(f"Received {count} records to update")

            # Use upsert for all insertions incase of retries
            self.upsert(insert_table, records_to_upsert)
            self.upsert(changes_table, changed_records)
            self.archive(insert_table, archive_field, existing_records_ids)

        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(
                f"An error occurred during update of listings on {insert_table}: {e}"
            )
            raise
        finally:
            self.session.close()
