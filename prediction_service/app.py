# pylint: disable=missing-module-docstring

import os
import threading
import time

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, request
from pandas import DataFrame
from prometheus_client import Counter, Summary, generate_latest, start_http_server

import mlflow
from utils.mlflow_utils import get_latest_model_from_registry
from utils.prometheus_utils import background_metrics_collector

# if running locally, try to load .env file
dotenv_path = find_dotenv(filename=".env", raise_error_if_not_found=False, usecwd=True)
load_dotenv(dotenv_path, override=True)

MLFLOW_TRACKING_URL = os.environ.get("MLFLOW_TRACKING_URL", "http://127.0.0.1:5001")
MLFLOW_MODEL_REGISTRY_NAME = os.environ.get(
    "MLFLOW_MODEL_REGISTRY_NAME", "wine_quality"
)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URL)
model = get_latest_model_from_registry(MLFLOW_MODEL_REGISTRY_NAME)

print("Starting Prometheus Service...")
start_http_server(9090)  # start prometheus server
print("Starting the service health metrics collection thread....")
metrics_thread = threading.Thread(target=background_metrics_collector)
metrics_thread.daemon = True
metrics_thread.start()
print("Thread started...")
REQUEST_LATENCY = Summary(
    "api_request_latency_seconds", "Latency of API requests", ["method", "endpoint"]
)
REQUEST_COUNT = Counter(
    "request_count", "Total request count", ["method", "endpoint", "http_status"]
)
MODEL_PERFORMANCE_TIME_SUMMARY = Summary(
    "model_performance_time_summary", "Model performance over time"
)


app = Flask("wine-quality-prediction")


@app.before_request
def before_request():
    """
    Record the start time of the request in order to calculate request latency
    """
    request.start_time = time.time()


@app.after_request
def after_request(response):
    """
    Send request related metrics to prometheus
    """
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.method, request.path).observe(latency)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()

    # if it's a prometheus request, we don't want to record the model performance
    if response.status_code == 200 and response.is_json:
        json_data = response.get_json()
        if json_data and "score" in json_data:
            MODEL_PERFORMANCE_TIME_SUMMARY.observe(json_data["score"])
    return response


@app.route("/predict", methods=["POST"])
def predict_endpoint():
    """ "
    Predict wine quality
    """
    request_input = request.get_json()
    score = model.predict(DataFrame([request_input]))[0]

    result = {"score": score}
    return jsonify(result)


@app.route("/metrics")
def metrics():
    """
    Explicitly expose prometheus metrics endpoint
    """
    return generate_latest()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9696)
