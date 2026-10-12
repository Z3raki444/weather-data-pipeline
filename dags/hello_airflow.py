import pendulum

from airflow.sdk import dag, task


@dag(
    dag_id="hello_airflow",
    schedule=None,
    start_date=pendulum.datetime(2026, 10, 1, tz="UTC"),
    catchup=False,
    tags=["learning"],
)
def hello_airflow():

    @task
    def say_hello():
        print("Hello from Airflow!")

    say_hello()


hello_airflow()