import json
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any
import copy
from confluent_kafka import Consumer, Producer
from .missing_data_handler import MissingDataHandler
from .prometheus import Prometheus


class KafkaDataProcessor:
    def __init__(
        self,
        consumer: Consumer,
        producer: Producer,
        data_handler: MissingDataHandler,
        prometheus: Prometheus,
    ):
        self.consumer = consumer
        self.data_handler = data_handler
        self.producer = producer
        self.prometheus = prometheus
        self.partitions = []

    def consume(self, topic: str):
        self.consumer.subscribe([topic])
        i = 1
        show_nf = True
        while True:
            msg = self.consumer.poll(10)
            self.partitions = self.consumer.assignment()

            if msg is None:
                if show_nf:
                    print("No message received :(")
                show_nf = False
                continue
            if msg.error():
                print(f"Error: {msg.error()}")
                continue

            show_nf = True
            value = pickle.loads(msg.value())
            value = json.loads(value)
            logvalue = copy.copy(value)
            logvalue["data"] = None

            if value["type"] == "start":
                print(i)
                self._start()
            if value["type"] == "stop":
                print(i)
                i = 1
                self._flush(sampling_rate=20)
            if value["type"] == "trace":
                i += 1
                len_data = value["len"]
                self.prometheus.inc_rec_data(len_data)
                start_pro = datetime.utcnow()
                self.__process_received_data(value, arrive_time=datetime.utcnow())
                end_pro = datetime.utcnow()
                self.prometheus.obs_proc_time((end_pro - start_pro).total_seconds())

    def __process_received_data(self, value: Dict[str, Any], arrive_time: datetime):
        station = value["station"]
        channel = value["channel"]
        eews_producer_time = value["eews_producer_time"]
        data = value["data"]
        start_time = datetime.fromisoformat(value["starttime"])
        end_time = datetime.fromisoformat(value["endtime"])
        sampling_rate = value["sampling_rate"]
        # if station == "BKB" and channel == "BHE":
        #     print("Received ", station, channel)
        #     print("from message: ", value['starttime'])

        # TODO: Comment this
        # self.producer.produce(
        #     station,
        #     channel,
        #     data,
        #     start_time,
        #     end_time,
        #     eews_producer_time=eews_producer_time,
        #     arrive_time=arrive_time,
        # )

        self.data_handler.handle_missing_data(
            station, channel, start_time, sampling_rate
        )
        self.__store_data(
            station,
            channel,
            data,
            start_time,
            sampling_rate,
            eews_producer_time=eews_producer_time,
            arrive_time=arrive_time,
        )

    def __store_data(
        self,
        station: str,
        channel: str,
        data: List[int],
        start_time: datetime,
        sampling_rate: float,
        eews_producer_time,
        arrive_time: datetime,
    ):
        # if station not in self.data_handler.data_pool:
        #     self.data_handler.data_pool[station] = {}
        # if channel not in self.data_handler.data_pool[station]:
        #     self.data_handler.data_pool[station][channel] = []

        current_time = start_time
        if (
            station in self.data_handler.last_processed_time
            and channel in self.data_handler.last_processed_time[station]
        ):
            current_time = self.data_handler.last_processed_time[station][channel]

        self.data_handler.data_pool[station][channel].extend(data)

        while len(self.data_handler.data_pool[station][channel]) >= 128:
            data_to_send = self.data_handler.data_pool[station][channel][:128]
            self.data_handler.data_pool[station][channel] = self.data_handler.data_pool[
                station
            ][channel][128:]
            time_to_add = timedelta(seconds=128 / sampling_rate)
            self.__send_data_to_queue(
                station,
                channel,
                data_to_send,
                current_time,
                current_time + time_to_add,
                eews_producer_time=eews_producer_time,
                arrive_time=arrive_time,
            )
            current_time = current_time + time_to_add

    def __send_data_to_queue(
        self,
        station: str,
        channel: str,
        data: List[int],
        start_time: datetime,
        end_time: datetime,
        eews_producer_time,
        arrive_time: datetime,
    ):
        self.data_handler.update_last_processed_time(station, channel, end_time)
        len_data = len(data)
        self.prometheus.inc_sent_data(len_data)
        self.producer.produce(
            station,
            channel,
            data,
            start_time,
            end_time,
            eews_producer_time=eews_producer_time,
            arrive_time=arrive_time,
        )

    def _start(self):
        # print("=" * 20, "START", "=" * 20)
        for i in self.partitions:
            self.producer.startTrace(i.partition)
        self.data_handler.reset_state()

    def _flush(self, sampling_rate):
        for station, stationDict in self.data_handler.data_pool.items():
            for channel, data_to_send in stationDict.items():
                end_time = self.data_handler.last_processed_time[station][channel]
                time_to_decrease = timedelta(seconds=len(data_to_send) / sampling_rate)
                start_time = end_time - time_to_decrease
                if station == "BKB" and channel == "BHE":
                    print("Flused ", station, channel, start_time, end_time)
                self.producer.produce(
                    station, channel, data_to_send, start_time, end_time
                )
        print("=" * 20, "END", "=" * 20)
        for i in self.partitions:
            self.producer.stopTrace(i.partition)
