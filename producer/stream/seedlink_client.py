from stream.client import StreamClient, StreamMode
from stream.producer import KafkaProducer
from obspy.clients.seedlink import EasySeedLinkClient
from obspy import Trace
import json
from datetime import datetime
from obspy.clients.seedlink.slpacket import SLPacket
from stream.const import StreamMode
from utils.redis_client import RedisSingleton
import copy

REPLICAS = 40


class SeedlinkClient(StreamClient, EasySeedLinkClient):
    def __init__(self, producer: KafkaProducer, server_url: str):
        self.server_url = server_url
        StreamClient.__init__(self, mode=StreamMode.LIVE, producer=producer)
        EasySeedLinkClient.__init__(self, server_url=self.server_url)
        self.__streaming_started = False
        print("Starting new seedlink client")
        for station in self.stations:
            self.select_stream(net="GE", station=station, selector="BH?")
        print("Starting connection to seedlink server ", self.server_hostname)

    def run(self):
        if not len(self.conn.streams):
            raise Exception(
                "No streams specified. Use select_stream() to select a stream"
            )
        self.__streaming_started = True
        # Start the collection loop
        print("Starting collection on:", datetime.utcnow())
        while True:
            arrive_time = datetime.utcnow()
            data = self.conn.collect()
            if data == SLPacket.SLTERMINATE:
                self.on_terminate()
                break
            elif data == SLPacket.SLERROR:
                self.on_seedlink_error()
                continue

            assert isinstance(data, SLPacket)
            packet_type = data.get_type()
            if packet_type not in (SLPacket.TYPE_SLINF, SLPacket.TYPE_SLINFT):
                trace = data.get_trace()
                self.on_data(trace, arrive_time=arrive_time)

    def startStreaming(self):
        self.producer.startTrace()
        print("-" * 20, "Streaming miniseed from seedlink server", "-" * 20)
        if not self.__streaming_started:
            self.run()

    def stopStreaming(self):
        self.producer.stopTrace()
        print("-" * 20, "Stopping miniseed", "-" * 20)

    def on_data(self, trace: Trace, arrive_time):
        arrive_time = datetime.utcnow()
        msg = self._extract_values(trace, arrive_time)
        self.producer.produce_message(json.dumps(msg), msg["station"], StreamMode.LIVE)
        station = msg["station"]
        for i in range(REPLICAS):
            repl_msg = copy.deepcopy(msg)
            repl_msg["station"] = f"{station}-{i}"
            self.producer.produce_message(
                json.dumps(repl_msg), repl_msg["station"], StreamMode.LIVE
            )
