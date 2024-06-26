# pylint: disable=missing-module-docstring
import json
import os
from time import sleep, time

import pandas as pd
import psutil
import requests
from prometheus_client import Gauge, Summary, start_http_server

PREDICTION_SERVICE_URL = os.environ.get(
    "PREDICTION_SERVICE_URL", "http://localhost:9696"
)


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


def simulate_api_request():
    """Simulate request processing for collecting health metrics"""
    sample_data = json.dumps(
        {
            "fixed_acidity": 7.4,
            "volatile_acidity": 0.7,
            "citric_acid": 0.0,
            "residual_sugar": 1.9,
            "chlorides": 0.076,
            "free_sulfur_dioxide": 11.0,
            "total_sulfur_dioxide": 34.0,
            "density": 0.9978,
            "pH": 3.51,
            "sulphates": 0.56,
            "alcohol": 9.4,
        }
    )
    url_api = f"{PREDICTION_SERVICE_URL}/predict"
    # print("Getting prediction...")
    headers = {"Content-Type": "application/json"}

    start_time = time()
    # Simulate request processing
    _ = requests.post(url_api, data=sample_data, headers=headers, timeout=5)
    return time() - start_time


def background_metrics_collector():
    """Collect system metrics in the background"""
    print("START PROMETHEUS SERVER")
    start_http_server(9090)  # start prometheus server
    request_latency = Summary("api_request_latency_seconds", "Latency of API requests")
    cpu_usage = Gauge("cpu_usage", "CPU usage percentage")
    memory_usage = Gauge("memory_usage", "Memory usage in bytes")
    disk_usage = Gauge("disk_usage", "Disk usage percentage")
    while True:
        print("Collecting metrics...")
        latency = simulate_api_request()
        request_latency.observe(latency)
        cpu_percent_measure = psutil.cpu_percent()
        memory_bytes_measure = psutil.virtual_memory().used
        disk_percent_measure = psutil.disk_usage("/").percent
        cpu_usage.set(cpu_percent_measure)
        memory_usage.set(memory_bytes_measure)
        disk_usage.set(disk_percent_measure)
        sleep(5)  # wait 5 seconds to collect the next data
