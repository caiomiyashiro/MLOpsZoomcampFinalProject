# pylint: disable=missing-module-docstring

import logging
import os
import pickle
import threading
import time
from time import sleep

from dotenv import find_dotenv, load_dotenv
from flask import Flask, jsonify, request
from pandas import DataFrame
from prometheus_client import Counter, Summary, generate_latest, start_http_server

import mlflow
from utils.mlflow_utils import get_latest_model_from_registry
from utils.prometheus_utils import background_metrics_collector

sleep(5)
# if running locally, try to load .env file
dotenv_path = find_dotenv(filename=".env", raise_error_if_not_found=False, usecwd=True)
load_dotenv(dotenv_path, override=True)

MLFLOW_TRACKING_URL = os.environ.get("MLFLOW_TRACKING_URL", "http://127.0.0.1:5001")
MLFLOW_MODEL_REGISTRY_NAME = os.environ.get(
    "MLFLOW_MODEL_REGISTRY_NAME", "wine_quality"
)
logging.info("--- Loaded MLFLOW_TRACKING_URL: %s", MLFLOW_TRACKING_URL)
logging.info("--- Loaded MLFLOW_MODEL_REGISTRY_NAME: %s", MLFLOW_MODEL_REGISTRY_NAME)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URL)
# try download model from registry. If it fails, load sample model.
# first time this service is run in docker-compose, the model will not be
# registered yet, so we load a sample model.
try:
    model = get_latest_model_from_registry(MLFLOW_MODEL_REGISTRY_NAME)
    print(
        f"---------- Registry {MLFLOW_MODEL_REGISTRY_NAME} found. Loading model...",
        flush=True,
    )
except (mlflow.exceptions.RestException, mlflow.exceptions.MlflowException) as e:
    logging.warning(
        "------ Registry model not loaded: %s ------\n. \
          Loading sample model. \
          Please make sure the model is registered in the provided \
          MLflow registry.",
        e,
    )
    with open("sample_model.pkl", "rb") as f:
        model = pickle.load(f)
        print("------ Loaded sample model", flush=True)


logging.info("Starting Prometheus Service...")
start_http_server(9090)  # start prometheus server
logging.info("Starting the service health metrics collection thread....")
metrics_thread = threading.Thread(target=background_metrics_collector)
metrics_thread.daemon = True
metrics_thread.start()
logging.info("Thread started...")
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
    # print("----------------------------------------1", flush=True)
    # print(f"{model.predict(DataFrame([request_input]))}", flush=True)
    # print("----------------------------------------", flush=True)
    # print(model.get_params, flush=True)

    score = model.predict(DataFrame([request_input]))[0]

    result = {"score": score}
    return jsonify(result)


@app.route("/metrics")
def metrics():
    """
    Explicitly expose prometheus metrics endpoint
    """
    return generate_latest()


@app.route("/healthcheck")
def healthcheck():
    """
    Healtcheck endpoint
    """
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9696)
