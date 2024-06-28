# pylint: disable=missing-module-docstring
import logging
import os

from dotenv import find_dotenv, load_dotenv
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

import mlflow

dotenv_path = find_dotenv(filename=".env", raise_error_if_not_found=True, usecwd=True)
load_dotenv(dotenv_path, override=True)  # Load variables from .env file

MLFLOW_EXPERIMENT_NAME = os.environ.get(
    "MLFLOW_EXPERIMENT_NAME", "wine_quality_hyperparameter_optimization"
)
MLFLOW_TRACKING_URL = os.environ.get("MLFLOW_TRACKING_URL", "http://localhost:5001")
MLFLOW_MODEL_REGISTRY_NAME = os.environ.get(
    "MLFLOW_MODEL_REGISTRY_NAME", "wine_quality"
)
logging.info("--- Loaded MLFLOW_EXPERIMENT_NAME: %s", {MLFLOW_EXPERIMENT_NAME})
logging.info("--- Loaded MLFLOW_TRACKING_URL: %s", MLFLOW_TRACKING_URL)
logging.info("--- Loaded MLFLOW_MODEL_REGISTRY_NAME: %s", MLFLOW_MODEL_REGISTRY_NAME)

mlflow.set_tracking_uri(MLFLOW_TRACKING_URL)
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)


def run_register_top_model():
    """
    Retrieves the top model run from the experiment, and registers the best model.
    """

    client = MlflowClient()

    # Retrieve the top_n model runs and log the models
    experiment = client.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    best_run = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=1,
        order_by=["metrics.training_root_mean_squared_error ASC"],
    )[0]

    # Register the best model
    model_uri = f"runs:/{best_run.info.run_id}/artifacts/MLmodel"
    mlflow.register_model(model_uri, MLFLOW_MODEL_REGISTRY_NAME)


if __name__ == "__main__":
    run_register_top_model()
