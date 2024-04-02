from datetime import datetime
from typing import List, Dict, Optional

from airflow import DAG
from airflow.decorators import task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
# from airflow.operators.python import PythonOperator

from modules.applications_tracking.applications import scrape

DAG_ID = "applications_tracking_dag"

with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2024, 1, 1),
    schedule="@once",
    catchup=False,
) as dag:

    create_applications_tables = SQLExecuteQueryOperator(task_id="create_applications_tables",
                                     conn_id="pg_conn",
                                     sql="sql/applications_tables_schemas.sql",)
    
    
    create_applications_tables

    # create_applications_tables = PostgresOperator(
    #     task_id="create_applications_tables",
    #     postgres_conn_id="pg_conn",
    #     sql="sql/applications_tables_schemas.sql",
    # )

    # @task()
    # def extract() -> Optional[List[Dict]]:
    #     url = "https://www.halifax.ca/business/planning-development/applications"

    #     ...


# Extract task gets the data

#  Transform task cleans up any formatting

# Load saves it to the db

    # populate_pet_table = PostgresOperator(
    #     task_id="populate_pet_table",
    #     sql="""
    #         INSERT INTO pet (name, pet_type, birth_date, OWNER)
    #         VALUES ( 'Max', 'Dog', '2018-07-05', 'Jane');
    #         INSERT INTO pet (name, pet_type, birth_date, OWNER)
    #         VALUES ( 'Susie', 'Cat', '2019-05-01', 'Phil');
    #         INSERT INTO pet (name, pet_type, birth_date, OWNER)
    #         VALUES ( 'Lester', 'Hamster', '2020-06-23', 'Lily');
    #         INSERT INTO pet (name, pet_type, birth_date, OWNER)
    #         VALUES ( 'Quincy', 'Parrot', '2013-08-11', 'Anne');
    #         """,
    #     postgres_conn_id="tutorial_pg_conn",
    # )
    # get_all_pets = PostgresOperator(
    #     task_id="get_all_pets",
    #     sql="SELECT * FROM pet;",
    #     postgres_conn_id="tutorial_pg_conn",
    # )

    # get_birth_date = PostgresOperator(
    #     task_id="get_birth_date",
    #     sql="SELECT * FROM pet WHERE birth_date BETWEEN SYMMETRIC %(begin_date)s AND %(end_date)s",
    #     parameters={"begin_date": "2020-01-01", "end_date": "2020-12-31"},
    #     hook_params={"options": "-c statement_timeout=3000ms"},
    #     postgres_conn_id="tutorial_pg_conn",
    # )

  # >> populate_pet_table >> get_all_pets >> get_birth_date
