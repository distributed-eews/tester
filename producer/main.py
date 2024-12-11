from fastapi import FastAPI, BackgroundTasks
from stream.manager import streamManager
from stream.client import StreamMode
from obspy import UTCDateTime
import uvicorn
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from stream.producer import kafkaProducer
import threading
from prometheus_client import Gauge, make_asgi_app, Info
import psutil
import time
from utils.d import d
import copy
import json
import pickle
import socket

SOURCE_MSEED = "20090118_064750.mseed"


load_dotenv()
app = FastAPI()
PORT = os.getenv("PORT")
REPLICAS = int(os.getenv("REPLICAS", 1))
PROMETHEUS_PORT = os.getenv("PROMETHEUS_PORT", 8001)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def gather_data():
    """Gathers the metrics"""

    hostname = socket.gethostname()

    # Create our collectors
    ram_metric = Gauge(
        "producer_memory_usage_bytes", "Memory usage in bytes.", ["hostname"]
    )
    cpu_metric = Gauge("producer_cpu_usage_percent", "CPU usage percent.", ["hostname"])
    cpu_core = Gauge(
        f"producer_cpu_core", "CPU core information.", ["core", "hostname"]
    )

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


@app.get("/test")
def testo(background_task: BackgroundTasks, replica: int = 1, partitions: int = 3):
    for i in range(0, partitions):
        kafkaProducer.producer.produce(
            topic="query",
            value=pickle.dumps(json.dumps({"type": "start"})),
            partition=i,
            key="start",
        )
    kafkaProducer.producer.flush()
    print("=" * 20, "Start Trace", "=" * 20)

    station = d["station"]
    kafkaProducer.produce_message(json.dumps(d), station)
    for i in range(int(replica)):
        repl_msg = copy.deepcopy(d)
        repl_msg["station"] = f"{station}-{i}"
        kafkaProducer.produce_message(json.dumps(repl_msg), repl_msg["station"])

    for i in range(0, partitions):
        kafkaProducer.producer.produce(
            topic="query",
            value=pickle.dumps(json.dumps({"type": "stop"})),
            partition=i,
            key="stop",
        )
    kafkaProducer.producer.flush()
    print("=" * 20, "Stop Trace", "=" * 20)
    return "ok"


@app.get("/playback")
def playback(
    background_task: BackgroundTasks,
    start_time: str | None = None,
    end_time: str | None = None,
):
    if start_time is None:
        # start_time = UTCDateTime("2023-10-22T20:00:00.00+07")
        start_time = UTCDateTime("2019-12-31T12:17:00.00+07")
    if end_time is None:
        end_time = UTCDateTime(start_time) + 60 * 7
    print(start_time)
    print(end_time)
    # streamManager.start(StreamMode.PLAYBACK, start_time, end_time)
    background_task.add_task(
        streamManager.start, StreamMode.PLAYBACK, start_time, end_time
    )
    return "ok"


@app.get("/live")
def live(background_task: BackgroundTasks):
    background_task.add_task(streamManager.start, StreamMode.LIVE)
    return "ok"


@app.get("/idle")
def live(background_task: BackgroundTasks):
    background_task.add_task(streamManager.start, StreamMode.IDLE)
    return "ok"


@app.get("/file")
def live(background_task: BackgroundTasks, filename: str = SOURCE_MSEED):
    background_task.add_task(streamManager.start, StreamMode.FILE, filename)
    return "ok"


metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


if __name__ == "__main__":
    # from multiprocessing import Pool

    # pool = Pool(2)
    # config = uvicorn.Config(
    #     "main:app", port=int(PORT), log_level="info", host="0.0.0.0"
    # )
    # server = uvicorn.Server(config)
    # pool.apply_async(server.run)
    # pool.apply_async(gather_data)

    # Create the thread that gathers the data while we serve it
    thread = threading.Thread(target=gather_data)
    thread.start()

    config = uvicorn.Config(
        "main:app", port=int(PORT), log_level="info", host="0.0.0.0"
    )
    server = uvicorn.Server(config)
    server.run()
