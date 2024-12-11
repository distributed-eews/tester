from stream.client import StreamClient, StreamMode
from stream.producer import KafkaProducer
import json
from datetime import datetime
from obspy import read, Stream, UTCDateTime, Trace
from stream.const import StreamMode
from utils.redis_client import RedisSingleton

class FileClient(StreamClient):
    def __init__(self, producer: KafkaProducer):
        self.producer = producer

    def startStreaming(self, file):
        self.producer.startTrace()
        self.stats: str = RedisSingleton().r.get("ENABLED_STATION_CODES")
        self.stations = set(self.stats.split(","))
        
        print("-"*20, "Streaming miniseed from file", "-"*20)
        st: Stream = read("./data/"+file)
        arrive_time = datetime.utcnow()
        for trace in st:
            if trace.stats.station not in self.stations:
                continue
            print(trace)            
            self.on_data(trace, arrive_time)

    def stopStreaming(self):
        self.producer.stopTrace()
        print("-"*20, "Stopping miniseed", "-"*20)

    def on_data(self, trace: Trace, arrive_time):
        arrive_time = datetime.utcnow()
        msg = self._extract_values(trace, arrive_time)
        self.producer.produce_message(json.dumps(msg), msg["station"], StreamMode.FILE)
