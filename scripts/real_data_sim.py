# pylint: disable=invalid-name,missing-module-docstring,import-error,wrong-import-position,no-name-in-module
import json
import os
import sys

# from utils.system_metrics import get_system_metrics
# from utils.evidently import send_data_row
import time

# import prometheus_client as pc
from datetime import datetime

import numpy as np
import pandas as pd
import psycopg2
import pytz
import requests
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine

# adding parent folder to sys.path to use utils folder functions
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from utils.dataset import get_dataset_ucirepo

# if running locally, try to load .env file
dotenv_path = find_dotenv(filename=".env", raise_error_if_not_found=False, usecwd=True)
# print(f"Loading .env file from: {dotenv_path}")
load_dotenv(dotenv_path, override=True)

# POSTGRES CREDENTIALS
POSTGRES_USER = os.environ.get("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "admin")
POSTGRES_DB = os.environ.get("POSTGRES_DB", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "127.0.0.1")
POSTGRES_TABLE = os.environ.get("POSTGRES_TABLE", "wine_quality")
url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}"
ENGINE = create_engine(f"{url}")

# PREDICTION SERVICE DATA
PREDICTION_SERVICE_URL = os.environ.get(
    "PREDICTION_SERVICE_URL", "http://127.0.0.1:9696"
)

# DATA TIMEZONE
DATA_TIMEZONE = os.environ.get("DATA_TIMEZONE", "Japan")


def recreate_empty_table() -> None:
    """
    Recreate the table in the database.
    This is just a test function to recreate the table in the database
    and simulate real data insertion.
    """
    conn = psycopg2.connect(
        host=f"{POSTGRES_HOST}",
        database=f"{POSTGRES_DB}",
        user=f"{POSTGRES_USER}",
        password=f"{POSTGRES_PASSWORD}",
    )

    cursor = conn.cursor()

    # Create a table with the desired columns
    # Add other table creation queries if needed
    create_table_query = """

        DROP TABLE IF EXISTS wine_quality;

        CREATE TABLE wine_quality (
            fixed_acidity FLOAT,
            volatile_acidity FLOAT,
            citric_acid FLOAT,
            residual_sugar FLOAT,
            chlorides FLOAT,
            free_sulfur_dioxide FLOAT,
            total_sulfur_dioxide FLOAT,
            density FLOAT,
            "pH" FLOAT,
            sulphates FLOAT,
            alcohol FLOAT,
            score FLOAT,
            time TIMESTAMP
        );
        """
    cursor.execute(create_table_query)
    conn.commit()


def get_prediction(data_row: pd.Series) -> float:
    """
    Get the prediction from the Prediction Service.
    Parameters:
        data_row (pd.Series): The row of data to predict.
    Returns:
        float: The prediction score.
    """
    data = data_row.to_dict()
    req_data = json.dumps(data)
    url_api = f"{PREDICTION_SERVICE_URL}/predict"
    # print("Getting prediction...")
    headers = {"Content-Type": "application/json"}
    response = requests.post(url_api, data=req_data, headers=headers, timeout=5)
    return response.json()["score"]


def main(X: pd.DataFrame, y: pd.DataFrame):
    # pylint: disable=unused-argument
    """
    Main function to simulate real-time data insertion into a PostgreSQL database
    and send data to MLflow tracking server.
    Parameters:
        X (pd.DataFrame): The features of the dataset.
        y (pd.DataFrame): The targets of the dataset.
    """
    index = 0
    while index < X.shape[0]:  # while all rows haven't been processed

        df_row = X.iloc[index].copy()  # get one row of data

        score = get_prediction(df_row)
        df_row["score"] = score
        tz = pytz.timezone(DATA_TIMEZONE)  # set timezone
        df_row["time"] = datetime.now(tz)  # simulate that data is from now

        index += 1  # update the index
        df_row = df_row.to_frame().T  # convert to DataFrame
        # print('Storing into database...')
        df_row.to_sql(POSTGRES_TABLE, ENGINE, if_exists="append", index=False)
        # sort a continuous positive number with uniform distribution using numpy
        wait_time = np.random.uniform(0, 1)

        # _ = get_system_metrics()

        time.sleep(wait_time)


if __name__ == "__main__":
    # logging.info("Waiting of the database to start...")
    time.sleep(10)  # wait for the database to start
    X_, y_ = get_dataset_ucirepo(repo_id=186)  # get wine dataset
    recreate_empty_table()  # recreate the table in the database
    main(X_, y_)
