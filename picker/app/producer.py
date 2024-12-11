import json
import os
from confluent_kafka import Producer
from dotenv import load_dotenv
from typing import Any

load_dotenv()

TOPIC_PRODUCER = os.getenv('TOPIC_PRODUCER')


class KafkaProducer:
    def __init__(self, bootstrap_servers):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})

    def produce(self, data: dict[str, Any]):
        station = data['station']
        print(f"DATA TO PRODUCE: {data}", end="\n")
        self.producer.produce(TOPIC_PRODUCER, key=station,
                              value=json.dumps(data))
