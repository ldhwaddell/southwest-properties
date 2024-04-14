from datetime import datetime, timedelta

from airflow import DAG
from airflow.decorators import task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from modules.applications_tracking.applications import scrape
from modules.database.database import Database
from modules.database.models import Application, ApplicationHistory, ScrapedApplication

DAG_ID = "applications_tracking_dag"

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

    create_applications_tables = SQLExecuteQueryOperator(
        task_id="create_applications_tables",
        conn_id="aws_postgres",
        sql="sql/applications_tables_schemas.sql",
    )
    create_applications_tables.doc_md = "Creates the necessary 'applications', 'scraped_applications', and 'applications_histories' tables if they do not exist"

    @task(task_id="extract", retries=3)
    def extract():
        """Extracts new application data by scraping and upserts into the DB."""

        url = "https://www.halifax.ca/business/planning-development/applications"
        db = Database()
        applications = scrape(url)
        db.upsert(ScrapedApplication, applications)

    @task(task_id="compare_and_update", retries=3)
    def compare_and_update():
        """Compare scraped applications with those from DB, save any changes"""
        db = Database()
        scraped_applications = db.select_all(ScrapedApplication)
        active_applications = db.get(Application, Application.active, True)
        db.update_records(
            Application,
            ApplicationHistory,
            Application.active,
            scraped_applications,
            active_applications,
        )

    drop_scraped_applications_table = SQLExecuteQueryOperator(
        task_id="drop_scraped_applications_table",
        conn_id="aws_postgres",
        sql="DROP TABLE scraped_applications;",
    )
    drop_scraped_applications_table.doc_md = "Drops the scraped_applications table."

    # Define the tasks
    extract_task = extract()
    compare_and_update_task = compare_and_update()

    # Set the task dependencies
    (
        create_applications_tables
        >> extract_task
        >> compare_and_update_task
        >> drop_scraped_applications_table
    )
