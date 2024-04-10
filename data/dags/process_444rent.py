from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from modules.rental_tracking.fourfourfourrent import scrape
from modules.database.database import Database

DAG_ID = "444rent_listings_tracking_dag"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
) as dag:

    create_listings_tables = SQLExecuteQueryOperator(
        task_id="create_listings_tables",
        conn_id="pg_conn",
        sql="sql/fourfourfourrent_tables_schemas.sql",
    )
    create_listings_tables.doc_md = "Creates the necessary 'fourfourfourrent_listings', 'scraped_fourfourfourrent_listings', and 'fourfourfourrent_listings_histories' tables if they do not exist"

    @task(task_id="extract", retries=3)
    def extract():
        """Extracts new listing data by scraping and upserts into the DB."""

        url = "https://www.444rent.com/apartments.asp"
        db = Database()
        listings = scrape(url)
        db.upsert("scraped_fourfourfourrent_listings", listings)

    # @task(task_id="compare_and_update", retries=3)
    # def compare_and_update():
    #     """Compare scraped applications with those from DB, save any changes"""
    #     db = Database()
    #     scraped_applications = db.get_scraped_applications()
    #     active_applications = db.get_active_applications()
    #     db.update(scraped_applications, active_applications)

    # drop_scraped_applications_table = SQLExecuteQueryOperator(
    #     task_id="drop_scraped_applications_table",
    #     conn_id="pg_conn",
    #     sql="DROP TABLE scraped_applications;",
    # )
    # drop_scraped_applications_table.doc_md = "Drops the scraped_applications table."

    # Define the tasks
    extract_task = extract()
    # compare_and_update_task = compare_and_update()

    # Set the task dependencies
    create_listings_tables >> extract_task
    # (
    #     create_applications_tables
    #     >> extract_task
    #     >> compare_and_update_task
    #     >> drop_scraped_applications_table
    # )
    
