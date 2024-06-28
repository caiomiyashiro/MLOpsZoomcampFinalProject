# pylint: disable=missing-module-docstring
from time import sleep

import psutil
from prometheus_client import Gauge


def background_metrics_collector():
    """Collect system metrics in the background"""
    cpu_usage = Gauge("cpu_usage", "CPU usage percentage")
    memory_usage = Gauge("memory_usage", "Memory usage in bytes")
    disk_usage = Gauge("disk_usage", "Disk usage percentage")
    while True:
        print("Collecting metrics...")
        cpu_percent_measure = psutil.cpu_percent()
        memory_bytes_measure = psutil.virtual_memory().used
        disk_percent_measure = psutil.disk_usage("/").percent
        cpu_usage.set(cpu_percent_measure)
        memory_usage.set(memory_bytes_measure)
        disk_usage.set(disk_percent_measure)
        sleep(5)  # wait 5 seconds to collect the next data
