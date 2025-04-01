import base64
import os
from datetime import datetime, timedelta

import boto3
from airflow import DAG, settings
from airflow.models import Connection
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.ecr import EcrHook
from airflow.providers.docker.operators.docker import DockerOperator
from dopplersdk import DopplerSDK

# Initialize and authenticate the Doppler SDK.
DOPPLER_TOKEN = os.getenv("DOPPLER_SERVICE_TOKEN")
doppler = DopplerSDK()
doppler.set_access_token(DOPPLER_TOKEN)

# Retrieve secrets from Doppler.
secrets = doppler.secrets.list(project="tsa", config="prd").secrets
ECR_REPOSITORY_NAME = secrets.get("ECR_REPOSITORY_NAME", {}).get("computed")
AWS_ECR_LOGIN_URI = secrets.get("AWS_ECR_LOGIN_URI", {}).get("computed")
AWS_REGION = secrets.get("AWS_REGION", {}).get("computed")

IMAGE = f"{AWS_ECR_LOGIN_URI}/{ECR_REPOSITORY_NAME}:latest"


def update_ecr_credentials():
    """
    Retrieve the AWS ECR authorization token and update the Airflow Docker connection.
    """
    # Initialize the ECR hook with the specified region.
    hook = EcrHook(aws_conn_id="aws_default", region_name=AWS_REGION)
    response = hook.get_client_type().get_authorization_token()
    auth_data = response["authorizationData"][0]

    # Decode the token that is in the format "username:password".
    token = base64.b64decode(auth_data["authorizationToken"]).decode("utf-8")
    username, password = token.split(":")
    registry_url = auth_data["proxyEndpoint"]

    # Create or update the Docker connection for ECR with new credentials.
    conn = Connection(
        conn_id="docker_ecr",
        conn_type="docker",
        host=registry_url,
        login=username,
        password=password,
    )
    session = settings.Session()

    try:
        session.query(Connection).filter(Connection.conn_id == "docker_ecr").delete()
        session.add(conn)
        session.commit()
    finally:
        session.close()


default_args = {
    "owner": "aritraganguly",
    "depends_on_past": False,
    "email": ["aritraganguly.in@protonmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
    "start_date": datetime(2025, 3, 5),
}

with DAG(
    "tsa_checkpoint_travel_dag",
    description="Orchestrate ETL Pipeline to scrape data from the TSA website.",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
    tags=["checkpoint_travel", "tsa"],
) as dag:

    update_ecr_credentials_task = PythonOperator(
        task_id="update_ecr_credentials", python_callable=update_ecr_credentials
    )

    tsa_numbers = DockerOperator(
        task_id="tsa_numbers",
        image=IMAGE,
        command=["/bin/bash", "-cx", "run_travel_numbers --environment prod"],
        environment={"DOPPLER_SERVICE_TOKEN": DOPPLER_TOKEN},
        docker_conn_id="docker_ecr",
        auto_remove="success",
        network_mode="bridge",
        api_version="auto",
        cpus=1,
        mem_limit="512m",
        force_pull=True,
    )

    update_ecr_credentials_task >> tsa_numbers
