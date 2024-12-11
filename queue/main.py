import os
from app.container import KafkaContainer
from dotenv import load_dotenv
import psutil
from prometheus_client import Gauge, Info
import time
import threading
import socket

load_dotenv()

BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS")
TOPIC_CONSUMER = os.getenv("TOPIC_CONSUMER")
PROMETHEUS_ADDR = os.getenv("PROMETHEUS_ADDR", "0.0.0.0")
PROMETHEUS_PORT = os.getenv("PROMETHEUS_PORT", "8012")


def gather_data():
    """Gathers the metrics"""

    # Create our collectors
    hostname = socket.gethostname()
    ram_metric = Gauge(
        f"queue_memory_usage_bytes", "Memory usage in bytes.", ["hostname"]
    )
    cpu_metric = Gauge(f"queue_cpu_usage_percent", "CPU usage percent.", ["hostname"])
    cpu_core = Gauge(f"queue_cpu_core", "CPU core information.", ["core", "hostname"])

    # Start gathering metrics every second
    while True:
        time.sleep(1)

        # Add ram metrics
        ram = psutil.virtual_memory()
        # swap = psutil.swap_memory()

        ram_metric.labels(hostname=hostname).set(ram.used)

        # Add cpu metrics
        cput = 0
        cpuc = 0
        for c, p in enumerate(psutil.cpu_percent(interval=1, percpu=True)):
            cpuc = cpuc + 1
            cput = cput + p
            cpu_core.labels(core=f"{c}", hostname=hostname).set(p)

        p = 0
        if cpuc > 0:
            p = cput / cpuc
        cpu_metric.labels(hostname=hostname).set(p)


if __name__ == "__main__":
    container = KafkaContainer()
    container.config.from_dict(
        {
            "bootstrap_servers": BOOTSTRAP_SERVERS,
            "kafka_config": {
                "bootstrap.servers": BOOTSTRAP_SERVERS,
                "group.id": "queue",
                "auto.offset.reset": "latest",
            },
            "prometheus": {
                "addr": PROMETHEUS_ADDR,
                "port": int(PROMETHEUS_PORT),
            },
        },
        True,
    )
    thread = threading.Thread(target=gather_data)
    thread.start()
    promethues = container.prometheus()
    promethues.start()
    data_processor = container.data_processor()
    print("=" * 20 + f"Consuming Data From {TOPIC_CONSUMER} Topic" + "=" * 20)
    data_processor.consume(TOPIC_CONSUMER)
