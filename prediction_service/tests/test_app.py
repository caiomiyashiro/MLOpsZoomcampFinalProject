# pylint: disable=missing-module-docstring
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(scope="module")
@patch("utils.mlflow_utils.get_latest_model_from_registry")
def patched_app(mock_get_model):
    # pylint: disable=import-outside-toplevel
    """
    Fixture to patch the Flask app.
    Before importing the app, we patch the `get_latest_model_from_registry` function
    """
    # mock get_latest_model_from_registry
    mock_model = MagicMock()
    mock_model.predict.return_value = [5.0]
    mock_get_model.return_value = mock_model

    # Import app after patching
    from app import app

    return app


@pytest.fixture(scope="module")
def client(patched_app):
    # pylint: disable=redefined-outer-name
    """Fixture to create a test client for the Flask app."""
    if patched_app is None:
        pytest.fail("patched_app is None. Check the patched_app fixture.")

    patched_app.config["TESTING"] = True
    with patched_app.test_client() as client_:
        # print("Yielding client")
        yield client_
    # print("Client fixture teardown")


def test_predict_endpoint(client):
    #  pylint: disable=redefined-outer-name
    """
    Test the predict endpoint of the Flask app.

    This test checks if:
    1. The endpoint responds with 200 status code
    2. The response contains a 'score' key
    3. The score is a float
    """

    input_json = {
        "fixed_acidity": 7.4,
        "volatile_acidity": 0.7,
        "citric_acid": 0,
        "residual_sugar": 1.9,
        "chlorides": 0.076,
        "free_sulfur_dioxide": 11,
        "total_sulfur_dioxide": 34,
        "density": 0.9978,
        "pH": 3.51,
        "sulphates": 0.56,
        "alcohol": 9.4,
    }
    response = client.post("/predict", json=input_json)
    assert response.status_code == 200
    assert "score" in response.json
    assert isinstance(response.json["score"], float)
    assert response.json["score"] == 5.0


def test_metrics_endpoint(client):
    #  pylint: disable=redefined-outer-name
    """
    Test the metrics endpoint of the Flask app.

    This test checks if:
    1. The endpoint responds with 200 status code
    2. The response contains prometheus metrics
    """
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"# HELP" in response.data  # Prometheus metrics usually start with "# HELP"
