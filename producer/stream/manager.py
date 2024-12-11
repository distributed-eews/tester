from stream.producer import KafkaProducer, kafkaProducer
from stream.fdsnws_client import FdsnwsClient
from stream.seedlink_client import SeedlinkClient
from stream.file_client import FileClient
from stream.const import StreamMode
from utils.redis_client import RedisSingleton


class StreamManager:
    def __init__(self, producer: KafkaProducer, fdsnws_server: str, seedlink_server: str):
        self.producer = producer
        self.fdsnws_server = fdsnws_server
        self.seedlink_server = seedlink_server
        self.fdsnws = FdsnwsClient(self.producer, base_url=self.fdsnws_server)
        self.seedlink = SeedlinkClient(
            self.producer, server_url=self.seedlink_server)
        self.fileclient = FileClient(self.producer)

    def start(self, mode: StreamMode, *args, **kwargs):
        if self.fdsnws.blocked:
            print("Blocked")
            return
        if mode == StreamMode.PLAYBACK:
            try:
                self.producer.current_mode = StreamMode.PLAYBACK
                self.fdsnws.startStreaming(*args, **kwargs)
            except Exception as err:
                print(err)
            finally:
                self.fdsnws.stopStreaming()
                self.producer.current_mode = StreamMode.IDLE

        if mode == StreamMode.FILE:
            try:
                self.producer.current_mode = StreamMode.FILE
                self.fileclient.startStreaming(*args, **kwargs)
            except Exception as err:
                print(err)
            finally:
                self.fileclient.stopStreaming()
                self.producer.current_mode = StreamMode.IDLE

        elif mode == StreamMode.LIVE and self.producer.current_mode == StreamMode.IDLE:
            self.producer.current_mode = StreamMode.LIVE
            self.seedlink.startStreaming()

        elif mode == StreamMode.IDLE: # stop live mode
            self.producer.current_mode = StreamMode.IDLE
            self.seedlink.stopStreaming()
        print(self.producer.current_mode)




streamManager = StreamManager(
    producer=kafkaProducer, fdsnws_server="GEOFON", seedlink_server="geofon.gfz-potsdam.de:18000")
