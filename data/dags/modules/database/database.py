import logging
import os
from typing import List, Dict, Type, Set

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

# from sqlalchemy import select, insert, update, bindparam

# from modules.database.models import Application

# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


class Database:
    def __init__(self):
        postgres_pass = os.environ.get("POSTGRES_PASSWORD")
        db_url = f"postgresql+psycopg2://airflow:southwest2024@postgres:5432/airflow"
        self.engine = create_engine(db_url)
        self.session_maker = sessionmaker(bind=self.engine)
        self.session: Session = self.session_maker()

    def insert_applications(self, applications: List[dict]):
        """Upserts applications into the applications table using raw SQL."""
        upsert_statement = text("""
            INSERT INTO applications (id, active, created_at, url, title, summary, last_updated, update_notice, request, proposal, process, status, documents_submitted_for_evaluation, contact_info)
            VALUES (:id, :active, COALESCE(:created_at, NOW()), :url, :title, :summary, :last_updated, :update_notice, :request, :proposal, :process, :status, :documents_submitted_for_evaluation, :contact_info)
            ON CONFLICT (id) DO UPDATE SET
                active = EXCLUDED.active,
                created_at = EXCLUDED.created_at,
                url = EXCLUDED.url,
                title = EXCLUDED.title,
                summary = EXCLUDED.summary,
                last_updated = EXCLUDED.last_updated,
                update_notice = EXCLUDED.update_notice,
                request = EXCLUDED.request,
                proposal = EXCLUDED.proposal,
                process = EXCLUDED.process,
                status = EXCLUDED.status,
                documents_submitted_for_evaluation = EXCLUDED.documents_submitted_for_evaluation,
                contact_info = EXCLUDED.contact_info;
        """)

        try:
            for application in applications:
                self.session.execute(upsert_statement, params=application)
            self.session.commit()
            logging.info(
                f"Successfully upserted {len(applications)} items into applications")
        except SQLAlchemyError as e:
            self.session.rollback()
            logging.error(
                f"An error occurred during application upsertion: {e}")

#     def get_active_applications(self) -> List[Application]:
#         """returns all applications where active is true"""
#         try:
#             query = select(Application).where(Application.active == True)
#             result = self.session.execute(query)

#             # return all results
#             return result.scalars().all()

#         except SQLAlchemyError as e:
#             logging.error(f"An error occurred during fetching active applications: {e}")
#             return []

#     def archive_applications(self, application_ids: Set[str]):
#         """Sets active to false for all the passed application ids"""
#         try:
#             query = (
#                 update(Application)
#                 .where(Application.id.in_(application_ids))
#                 .values(active=False)
#             )
#             result = self.session.execute(query)
#             self.session.commit()

#             logging.info(f"Successfully archived {result.rowcount} applications")

#         except SQLAlchemyError as e:
#             self.session.rollback()
#             logging.error(f"An error occurred during archiving applications: {e}")

#     def compare_application(self, scraped_application: Dict):
#         """Compares an existing record to the scraped one. Records any differences"""
#         try:
#             # Existing entry
#             query = select(Application).where(
#                 Application.id == scraped_application["id"]
#             )
#             existing_record = self.session.execute(query).scalar_one_or_none()

#             change_records: List[ApplicationHistory] = []

#             # Compare existing entry to keys from scraped application
#             for key, value in scraped_application.items():
#                 # Check if the attribute exists and has a different value
#                 if (
#                     hasattr(existing_record, key)
#                     and getattr(existing_record, key) != value
#                 ):
#                     # Record the change
#                     change_record = ApplicationHistory(
#                         application_id=existing_record.id,
#                         changed=key,
#                         original=str(getattr(existing_record, key)),
#                         updated=str(value),
#                     )

#                     # Update the DB record
#                     setattr(existing_record, key, value)

#                     change_records.append(change_record)

#             # If changes were detected, add them to the session and commit everything together
#             if change_records:
#                 self.session.add_all(change_records)
#                 self.session.commit()
#                 logging.info(
#                     f"{len(change_records)} changes detected and recorded for application ID {existing_record.id}."
#                 )

#         except SQLAlchemyError as e:
#             self.session.rollback()
#             logging.error(f"An error occurred while comparing applications: {e}")

#     def update(self, scraped_applications: List[Dict]):
#         """Updates the database based on scraped applications."""
#         try:
#             active_applications = self.get_active_applications()
#             active_applications_ids = set(app.id for app in active_applications)
#             applications_to_insert = []

#             for app in scraped_applications:
#                 if app["id"] in active_applications_ids:
#                     # Removing it from active ids means those left in active ids are inactive
#                     active_applications_ids.remove(app["id"])
#                     self.compare_application(app)

#                 else:
#                     # This means it is a new application
#                     applications_to_insert.append(Application(**app))

#             self.insert_applications(applications_to_insert)
#             self.archive_applications(active_applications_ids)

#         except Exception as e:
#             logging.error(f"An error occurred during update: {e}")
#         finally:
#             self.session.close()


# if __name__ == "__main__":
#     # db = Database("sqlite:///southwest.db")
#     db = Database("postgresql://airflow:airflow@localhost:5432/airflow")

#     db.create_tables()
#     db.show_tables()
