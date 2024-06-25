# pylint: disable=missing-module-docstring
import os

from dotenv import find_dotenv, load_dotenv
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

import mlflow

dotenv_path = find_dotenv(filename=".env", raise_error_if_not_found=True, usecwd=True)
load_dotenv(dotenv_path, override=True)  # Load variables from .env file

EXPERIMENT_NAME = os.environ.get(
    "EXPERIMENT_NAME", "wine_quality_hyperparameter_optimization"
)
TRACKING_URL = os.environ.get("TRACKING_URL", "http://localhost:5001")
MODEL_REGISTRY_NAME = os.environ.get("MODEL_REGISTRY_NAME", "wine_quality")

mlflow.set_tracking_uri(TRACKING_URL)
mlflow.set_experiment(EXPERIMENT_NAME)


def run_register_top_model():
    """
    Retrieves the top model run from the experiment, and registers the best model.
    """

    client = MlflowClient()

    # Retrieve the top_n model runs and log the models
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    best_run = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=1,
        order_by=["metrics.training_root_mean_squared_error DESC"],
    )[0]

    # Register the best model
    model_uri = f"runs:/{best_run.info.run_id}/artifacts/MLmodel"
    mlflow.register_model(model_uri, MODEL_REGISTRY_NAME)


if __name__ == "__main__":
    run_register_top_model()
