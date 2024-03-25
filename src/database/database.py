import logging

from typing import List, Dict, Type

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, NoResultFound


from .models import Base

# Set up logger
logger = logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)-8s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s",
)


class Database:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.session = sessionmaker(bind=self.engine)

    def create_tables(self):
        inspector = inspect(self.engine)
        existing_tables_before = inspector.get_table_names()

        try:
            Base.metadata.create_all(self.engine)
            existing_tables_after = inspector.get_table_names()
            created_tables = set(existing_tables_after) - set(existing_tables_before)
            if created_tables:
                logging.info(f"Successfully created tables: {created_tables}")
            else:
                logging.info("No new tables created; all tables already exist.")
        except SQLAlchemyError as e:
            logging.error(f"Error creating tables: {e}")

    def show_tables(self):
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        logging.info(f"Tables in the database: {tables}")

    def compare_and_insert(self, table_class, data_list: List[Dict]):
        session = self.session()
        new_records = []
        updated_records = 0

        try:
            for data in data_list:
                diff_fields = []
                try:
                    # Try to retrieve the existing record by id
                    existing_record = (
                        session.query(table_class).filter_by(id=data["id"]).one()
                    )
                    # Compare each field in the existing record with the new data
                    for key, value in data.items():
                        if getattr(existing_record, key) != value:
                            setattr(existing_record, key, value)
                            updated_records += 1
                    session.commit()
                except NoResultFound:
                    # If the record doesn't exist, prepare it for bulk insert
                    new_records.append(table_class(**data))

            if diff_fields:
                logging.info(f"Different fields found: {diff_fields}")

            # Bulk insert new records
            if new_records:
                session.bulk_save_objects(new_records)
                session.commit()
                logging.info(
                    f"Inserted {len(new_records)} new records into {table_class.__tablename__}."
                )
            if updated_records:
                logging.info(
                    f"Updated {updated_records} existing records in {table_class.__tablename__}."
                )

            if not new_records and not updated_records:
                logging.info(
                    f"No new or updated records in {table_class.__tablename__}."
                )

        except SQLAlchemyError as e:
            session.rollback()
            logging.error(
                f"Error in compare_and_insert for {table_class.__tablename__}: {e}"
            )
        finally:
            session.close()


if __name__ == "__main__":
    db = Database("sqlite:///southwest.db")
    db.create_tables()
