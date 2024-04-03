import logging
import os
from typing import List, Dict, Set

from sqlalchemy import create_engine, select, MetaData, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import insert

from modules.database.models import Application, ApplicationHistory, ScrapedApplication

# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


class Database:
    def __init__(self):
        postgres_pass = os.environ.get("POSTGRES_PASSWORD")
        logging.info(postgres_pass)
        db_url = f"postgresql+psycopg2://airflow:southwest2024@postgres:5432/airflow"
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

        # ScrapedApplicationTable = ScrapedApplication.__table__
        table = self.metadata.tables.get(table_name)
        if table is None:
            raise ValueError(
                f"Table '{table_name}' not found in the database.")

        try:
            for application_data in applications:
                # Use the table object for the insert statement
                insert_stmt = insert(table).values(
                    **application_data)

                do_update_stmt = insert_stmt.on_conflict_do_update(
                    # Assuming 'id' is the column you want to conflict on
                    index_elements=['id'],
                    set_={k: application_data[k]
                          for k in application_data if k != 'id'}
                )

                # Execute the upsert statement
                self.session.execute(do_update_stmt)

            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(
                f"An error occurred during application upsertion: {e}")
            raise

    def get_scraped_applications(self):
        """Fetches all records from the scraped_applications table."""
        try:
            applications = self.session.query(ScrapedApplication).all()
            return applications

        except SQLAlchemyError as e:
            logging.error(
                f"An error occurred while fetching scraped applications: {e}")
            raise

    def get_active_applications(self):
        """Fetches all active records from the applications table using ORM style."""
        try:
            # This is now consistent with get_scraped_applications
            active_applications = self.session.query(
                Application).filter(Application.active == True).all()
            return active_applications

        except SQLAlchemyError as e:
            logging.error(
                f"An error occurred while fetching active applications: {e}")
            raise

    def archive_applications(self, application_ids: Set[str]):
        """Sets active to false for all the passed application ids"""
        try:
            # Ensure there are IDs to process
            if application_ids:

                query = update(Application).where(
                    Application.id.in_(application_ids)).values(active=False)

                result = self.session.execute(query)
                self.session.commit()

                logging.info(
                    f"Successfully archived {result.rowcount} applications")
            else:
                logging.info("No applications to archive")

        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(
                f"An error occurred while archiving applications: {e}")
            raise

    def compare_application(self, scraped_application: ScrapedApplication):
        """Compares an existing record to the scraped one. Records any differences"""
        try:
            # Existing entry
            query = select(Application).where(
                Application.id == scraped_application.id
            )
            existing_record = self.session.execute(query).scalar_one_or_none()

            change_records: List[ApplicationHistory] = []

            application_data = {
                key: value for key, value in scraped_application.__dict__.items() if not key.startswith('_')}

            # Compare existing entry to keys from scraped application
            for key, value in application_data.items():
                # Skip created_at as it will always be different
                if key == "created_at":
                    continue

                # Check if the attribute exists and has a different value
                if (
                    hasattr(existing_record, key)
                    and getattr(existing_record, key) != value
                ):
                    # Record the change
                    change_record = ApplicationHistory(
                        application_id=existing_record.id,
                        changed=key,
                        original=str(getattr(existing_record, key)),
                        updated=str(value),
                    )

                    # Update the DB record
                    setattr(existing_record, key, value)

                    change_records.append(change_record)

            # If changes were detected, add them to the session and commit everything together
            if change_records:
                self.session.add_all(change_records)
                self.session.commit()
                logging.info(
                    f"{len(change_records)} changes detected and recorded for application ID {existing_record.id}."
                )

        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(
                f"An error occurred while comparing applications: {e}")
            raise

    def update(self, scraped_applications: List[ScrapedApplication], active_applications: List[Application]):
        """Updates the database based on scraped applications."""
        try:
            active_applications_ids = set(
                app.id for app in active_applications)

            applications_to_upsert = []

            for app in scraped_applications:
                application_data = {
                    key: value for key, value in app.__dict__.items() if not key.startswith('_')}

                if app.id in active_applications_ids:
                    # Removing it from active ids means those left in active ids are inactive
                    active_applications_ids.remove(app.id)
                    # Check for changes
                    self.compare_application(app)
                else:
                    # For new add them to the list for upsertion.
                    applications_to_upsert.append(application_data)

            self.upsert("applications", applications_to_upsert)
            self.archive_applications(active_applications_ids)

        except SQLAlchemyError as e:
            logging.error(f"An error occurred during update: {e}")
            raise
        finally:
            self.session.close()


if __name__ == "__main__":
    db = Database()
    db.update()
