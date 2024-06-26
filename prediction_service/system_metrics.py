# pylint: disable=missing-module-docstring
import prometheus_client as pc
import psutil

# # Update Gauge metrics
# cpu_usage.set(cpu_percent)
# memory_usage.set(memory_bytes)

# # Increment Counter metric
# requests_total.inc()

# # Track request latency using Summary metric
# @request_latency.time()
# def process_request():
#     # Your request processing code here
#     pass

pc.start_http_server(9696)

cpu_usage = pc.Gauge("cpu_usage", "CPU usage percentage")
memory_usage = pc.Gauge("memory_usage", "Memory usage in bytes")
disk_usage = pc.Gauge("disk_usage", "Disk usage percentage")


def get_system_metrics():
    """
    Get system metrics
    """
    cpu_percent = psutil.cpu_percent()
    memory_bytes = psutil.virtual_memory().used
    disk_percent = psutil.disk_usage("/").percent

    cpu_usage.set(cpu_percent)
    memory_usage.set(memory_bytes)
    disk_usage.set(disk_percent)

    return {
        "cpu_usage": cpu_percent,
        "memory_usage": memory_bytes,
        "disk_usage": disk_percent,
    }
