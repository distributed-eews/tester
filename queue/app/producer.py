from datetime import datetime
import json
import os
from confluent_kafka import Producer
from dotenv import load_dotenv
import copy

load_dotenv()

TOPIC_PRODUCER = os.getenv("TOPIC_PRODUCER")


class KafkaProducer:
    def __init__(self, bootstrap_servers):
        self.producer = Producer({"bootstrap.servers": bootstrap_servers})

    def produce(
        self,
        station,
        channel,
        data,
        start_time,
        end_time,
        eews_producer_time=None,
        arrive_time=datetime.utcnow(),
    ):
        if eews_producer_time is None:
            eews_producer_time = [
                arrive_time.isoformat(),
                datetime.utcnow().isoformat(),
            ]
        data = {
            "station": station,
            "channel": channel,
            "starttime": start_time.isoformat(),
            "endtime": end_time.isoformat(),
            "data": data,
            "len": len(data),
            "eews_producer_time": eews_producer_time,
            "eews_queue_time": [arrive_time.isoformat(), datetime.utcnow().isoformat()],
            "type": "trace",
        }
        # if station == "BKB" and channel == "BHE":
        #     print(("=" * 20) + f"{station}____{channel}" + ("="*20))
        #     print('packet time: ', [data['starttime'], data['endtime']])
        #     print('eews_producer_time: ', data['eews_producer_time'])
        #     print('eews_queue_time: ', data['eews_queue_time'])
        # log_data = copy.deepcopy(data)
        # log_data["data"] = None
        # print(("=" * 20) + f"{station}____{channel}" + ("=" * 20))
        # print(log_data)
        # print(("=" * 20) + f"{station}____{channel}" + ("="*20))
        print("Producing ", station, channel, len(data))
        self.producer.produce(TOPIC_PRODUCER, key=station, value=json.dumps(data))

    def startTrace(self, partition):
        self.producer.produce(
            topic=TOPIC_PRODUCER,
            key="start",
            value=json.dumps({"type": "start"}),
            partition=int(partition),
        )
        self.producer.flush()
        # print("=" * 20, "Start Trace ", partition, "=" * 20)

    def stopTrace(self, partition):
        self.producer.produce(
            topic=TOPIC_PRODUCER,
            key="stop",
            value=json.dumps({"type": "stop"}),
            partition=int(partition),
        )
        self.producer.flush()
        # print("=" * 20, "Stop Trace ", partition, "=" * 20)
