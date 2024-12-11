from stream.client import StreamClient, StreamMode
from stream.producer import KafkaProducer
from obspy.clients.fdsn import Client
from obspy import UTCDateTime, Trace
import logging
import json
from datetime import datetime
from stream.const import StreamMode
from utils.redis_client import RedisSingleton
import copy
from dotenv import load_dotenv
import os
from prometheus_client import Gauge, Histogram, Counter


PRODUCING_TIME_GAUGE = Gauge(
    "producer_producing_time", "Time taken to produce messages"
)
PRODUCING_TIME_HISTOGRAM = Histogram(
    "producer_producing_time_histogram", "Time taken to produce messages"
)
DATA_SENT_TOTAL = Counter("producer_data_sent_total", "Total data sent to kafka")
logger = logging.getLogger()
logger.setLevel(logging.INFO)
load_dotenv()

REPLICAS = int(os.getenv("REPLICAS", 1))


class FdsnwsClient(StreamClient, Client):
    def __init__(self, producer: KafkaProducer, base_url: str):
        StreamClient.__init__(self, mode=StreamMode.LIVE, producer=producer)
        Client.__init__(self, base_url=base_url)
        self.blocked = False

    def startStreaming(self, start_time, end_time):
        st = datetime.now()
        logging.info("Starting FDSN Client...")
        print(f"REPLICAS: {REPLICAS}")
        self.stats: str = RedisSingleton().r.get("ENABLED_STATION_CODES")
        self.stations = set(self.stats.split(","))

        self.producer.startTrace()
        self.blocked = True
        result = []
        res = self._bulk(start_time, end_time)
        arrive_time = datetime.utcnow()
        for trace in res:
            msg = self._extract_values(trace, arrive_time=arrive_time)
            self.producer.produce_message(
                json.dumps(msg), msg["station"], StreamMode.PLAYBACK
            )
            npts = trace.stats.npts
            DATA_SENT_TOTAL.inc(npts)
            station = msg["station"]
            print(f"Producing message for {station}")
            for i in range(REPLICAS):
                repl_msg = copy.deepcopy(msg)
                repl_msg["station"] = f"{station}-{i}"
                print(f"Producing message for {repl_msg['station']}")
                self.producer.produce_message(
                    json.dumps(repl_msg), repl_msg["station"], StreamMode.PLAYBACK
                )
                DATA_SENT_TOTAL.inc(npts)
        et = datetime.now()
        PRODUCING_TIME_GAUGE.set((et - st).total_seconds())
        PRODUCING_TIME_HISTOGRAM.observe((et - st).total_seconds())
        return result

    def stopStreaming(self):  # currently not supported to cancel midrequest
        logging.info("Stopping playback...")
        self.blocked = False
        self.producer.stopTrace()

    # def _produce_time_window(self, start_time, end_time):
    #     start_time = UTCDateTime(start_time)
    #     end_time = UTCDateTime(end_time)
    #     if (start_time >= end_time):
    #         raise ValueError("Start time is greater than end time")
    #     result = []
    #     pointer = start_time
    #     while (pointer < end_time):
    #         result.append(pointer)
    #         pointer += 30
    #     result.append(end_time)
    #     return result

    def _bulk(self, start_time, end_time):
        bulk = [
            ("GE", station, "*", "BH?", start_time, end_time)
            for station in self.stations
        ]
        result = self.get_waveforms_bulk(bulk=bulk)
        return result
