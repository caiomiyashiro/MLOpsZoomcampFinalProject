# pylint: disable=missing-module-docstring
from unittest.mock import MagicMock, mock_open, patch

import pytest

from utils.mlflow_utils import get_latest_model_from_registry


@pytest.fixture
def mock_mlflow_client():
    """
    Fixture to mock the MlflowClient class.
    """
    return MagicMock()


@patch("utils.mlflow_utils.MlflowClient")
@patch("utils.mlflow_utils.pickle.load")
@patch("builtins.open", new_callable=mock_open, read_data=b"mocked file contents")
def test_get_latest_model_from_registry(
    mock_file_open, mock_pickle_load, mock_mlflow_client_
):
    """
    Test the get_latest_model_from_registry function.

    This test checks if:
    1. The function calls MlflowClient correctly
    2. It downloads the artifacts
    3. It loads and returns the model
    """
    # Setup mocks
    mock_client = mock_mlflow_client_.return_value
    mock_latest_version = MagicMock()
    mock_latest_version.run_id = "test_run_id"
    mock_client.get_latest_versions.return_value = [mock_latest_version]
    mock_client.download_artifacts.return_value = "test_path"
    mock_model = MagicMock()
    mock_pickle_load.return_value = mock_model

    # Call the function
    result = get_latest_model_from_registry("test_registry", mock_client)

    # Assertions
    mock_client.get_latest_versions.assert_called_once_with("test_registry")
    mock_client.download_artifacts.assert_called_once_with(
        run_id="test_run_id", path="artifacts/model.pkl"
    )
    mock_file_open.assert_called_once_with("test_path", "rb")
    mock_pickle_load.assert_called_once()
    assert result == mock_model
