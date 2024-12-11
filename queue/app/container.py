from confluent_kafka import Consumer
from .producer import KafkaProducer
from .missing_data_handler import MissingDataHandler
from .processor import KafkaDataProcessor
from dependency_injector import containers, providers
from .prometheus import Prometheus


class KafkaContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    producer = providers.Singleton(
        KafkaProducer,
        bootstrap_servers=config.bootstrap_servers,
    )
    data_handler = providers.Singleton(MissingDataHandler)
    consumer = providers.Singleton(Consumer, config.kafka_config)
    prometheus = providers.Singleton(
        Prometheus, addr=config.prometheus.addr, port=config.prometheus.port
    )
    data_processor = providers.Singleton(
        KafkaDataProcessor,
        consumer=consumer,
        producer=producer,
        data_handler=data_handler,
        prometheus=prometheus,
    )
