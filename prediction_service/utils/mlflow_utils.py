# pylint: disable=missing-module-docstring

import logging
import pickle

from mlflow.tracking import MlflowClient


def get_latest_model_from_registry(
    registry_name: str = "wine_quality", client: MlflowClient = None
):
    """
    Get the latest model from the model registry.
    The function assumes that the tracking directory is already set, e.g.,
    `mlflow.set_tracking_uri(MLFLOW_TRACKING_URL)`
    Parameters:
        registry_name (str): The name of the model registry
        client (MlflowClient): An optional MlflowClient object
    """
    print("test")
    if client is None:
        client = MlflowClient()
    latest_model = client.get_latest_versions(registry_name)[-1]
    model_run_id = latest_model.run_id

    model_path = client.download_artifacts(
        run_id=model_run_id, path="artifacts/model.pkl"
    )
    logging.info("%s", "Model sucessfully downloaded")
    with open(model_path, "rb") as f:
        downloaded_model = pickle.load(f)
    return downloaded_model
