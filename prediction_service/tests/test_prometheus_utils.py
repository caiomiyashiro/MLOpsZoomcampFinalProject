# pylint: disable=invalid-name,missing-module-docstring,import-error,wrong-import-position,no-name-in-module
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from unittest.mock import MagicMock, patch

import pytest

from utils.prometheus_utils import background_metrics_collector


@patch("utils.prometheus_utils.psutil")
@patch("utils.prometheus_utils.Gauge")
@patch("utils.prometheus_utils.sleep")
def test_background_metrics_collector(mock_sleep, mock_gauge, mock_psutil):
    """
    Test the background_metrics_collector function.

    This test checks if:
    1. The function creates the correct Gauge metrics
    2. It collects system metrics using psutil
    3. It sets the Gauge values correctly
    4. It sleeps for the correct amount of time
    """
    # Setup mocks
    mock_cpu_gauge = MagicMock()
    mock_memory_gauge = MagicMock()
    mock_disk_gauge = MagicMock()
    mock_gauge.side_effect = [mock_cpu_gauge, mock_memory_gauge, mock_disk_gauge]

    mock_psutil.cpu_percent.return_value = 50.0
    mock_psutil.virtual_memory.return_value.used = 1000000
    mock_psutil.disk_usage.return_value.percent = 75.0

    # Call the function (it runs indefinitely, so we'll stop it after one iteration)
    mock_sleep.side_effect = StopIteration
    with pytest.raises(StopIteration):
        background_metrics_collector()

    # Assertions
    assert mock_gauge.call_count == 3
    mock_cpu_gauge.set.assert_called_once_with(50.0)
    mock_memory_gauge.set.assert_called_once_with(1000000)
    mock_disk_gauge.set.assert_called_once_with(75.0)
    mock_sleep.assert_called_once_with(5)
