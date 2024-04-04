import logging
import os
from typing import List, Dict, Set

from sqlalchemy import create_engine, select, MetaData, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import insert

from modules.database.models import Application, ScrapedApplication

# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


class Database:
    def __init__(self):
        db_url = os.environ.get("AIRFLOW__DATABASE__SQL_ALCHEMY_CONN")
        self.engine = create_engine(db_url)
        self.metadata = MetaData(bind=self.engine)
        self.metadata.reflect(bind=self.engine)
        self.session_maker = sessionmaker(bind=self.engine)
        self.session: Session = self.session_maker()

    def upsert(self, table_name: str, applications: List[Dict]):
        """
        Upserts applications into the applications table. Cannot do traditional insert as idempotency is
        required if task retries
        """
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise ValueError(f"Table '{table_name}' not found in the database.")

        logging.info(f"Received {len(applications)} items to upsert")

        try:

            for application_data in applications:
                # Use the table object for the insert statement
                insert_stmt = insert(table).values(**application_data)

                do_update_stmt = insert_stmt.on_conflict_do_update(
                    index_elements=["id"],
                    set_={
                        k: application_data[k] for k in application_data if k != "id"
                    },
                )

                # Execute the upsert statement
                self.session.execute(do_update_stmt)

            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"An error occurred during application upsertion: {e}")
            raise

    def get_scraped_applications(self):
        """Fetches all records from the scraped_applications table."""
        try:
            applications = self.session.query(ScrapedApplication).all()
            return applications

        except SQLAlchemyError as e:
            logging.error(f"An error occurred while fetching scraped applications: {e}")
            raise

    def get_active_applications(self):
        """Fetches all active records from the applications table using ORM style."""
        try:
            # This is now consistent with get_scraped_applications
            active_applications = (
                self.session.query(Application).filter(Application.active == True).all()
            )
            return active_applications

        except SQLAlchemyError as e:
            logging.error(f"An error occurred while fetching active applications: {e}")
            raise

    def archive_applications(self, application_ids: Set[str]):
        """Sets active to false for all the passed application ids"""
        try:
            # Ensure there are IDs to process
            if application_ids:

                query = (
                    update(Application)
                    .where(Application.id.in_(application_ids))
                    .values(active=False)
                )

                result = self.session.execute(query)
                self.session.commit()

                logging.info(f"Successfully archived {result.rowcount} applications")
            else:
                logging.info("No applications to archive")

        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"An error occurred while archiving applications: {e}")
            raise

    def compare_application(
        self, scraped_application: Dict
    ) -> List[Dict]:
        """Compares an existing record to the scraped one. Records any differences"""
        try:
            # Existing entry
            query = select(Application).where(
                Application.id == scraped_application["id"]
            )
            existing_record = self.session.execute(query).scalar_one_or_none()
            change_records: List[Dict] = []

            # Compare existing entry to keys from scraped application
            for key, value in scraped_application.items():

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

    def update(
        self,
        scraped_applications: List[ScrapedApplication],
        active_applications: List[Application],
    ):
        """Updates the database based on scraped applications."""
        try:
            active_applications_ids = set(app.id for app in active_applications)

            applications_to_upsert = []
            changed_records = []

            logging.info(f"Received {len(scraped_applications)} applications to update")

            for app in scraped_applications:
                application_data = {
                    key: value
                    for key, value in app.__dict__.items()
                    if not key.startswith("_")
                }

                if app.id in active_applications_ids:
                    # Removing it from active ids means those left in active ids are inactive
                    active_applications_ids.remove(app.id)

                    # Check for changes
                    changes = self.compare_application(application_data)
                    if changes:
                        changed_records.extend(changes)

                applications_to_upsert.append(application_data)

            # Use upsert for all insertions incase of retries
            self.upsert("applications", applications_to_upsert)
            self.upsert("application_histories", changed_records)
            self.archive_applications(active_applications_ids)

        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(f"An error occurred during update: {e}")
            raise
        finally:
            self.session.close()


if __name__ == "__main__":
    url = "https://www.halifax.ca/business/planning-development/applications"
    db = Database()
    scraped_applications = db.get_scraped_applications()
    active_applications = db.get_active_applications()

    db.update(scraped_applications, active_applications)
