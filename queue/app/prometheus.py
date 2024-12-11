from prometheus_client import start_http_server, Counter, Histogram, Gauge
import socket

hostname = socket.gethostname()


PROCESSING_TIME = Histogram(
    f"queue_processing_time", "Time spent processing", ["hostname"]
)
PROCESSING_TIME_GAUGE = Gauge(
    f"queue_processing_time_gauge", "Time spent processing", ["hostname"]
)
RECEIVED_DATA = Counter(f"queue_received_data", "Number of data received", ["hostname"])
SENT_DATA = Counter(f"queue_sent_data", "Number of data sent", ["hostname"])


class Prometheus:
    def __init__(self, port=8012, addr="0.0.0.0"):
        self.addr = addr
        self.port = port

    def start(self):
        start_http_server(self.port, self.addr)

    def inc_sent_data(self, inc=1):
        SENT_DATA.labels(hostname).inc(inc)

    def inc_rec_data(self, inc=1):
        RECEIVED_DATA.labels(hostname).inc(inc)

    def obs_proc_time(self, seconds: float):
        PROCESSING_TIME.labels(hostname).observe(seconds)
        PROCESSING_TIME_GAUGE.labels(hostname).set(seconds)
