from confluent_kafka import Consumer
from .producer import KafkaProducer
from .processor import KafkaDataProcessor
from .pooler import Pooler
from .myredis import MyRedis
from .mongo import MongoDBClient
from dependency_injector import containers, providers
from .prometheus import Prometheus


class KafkaContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    producer = providers.Singleton(
        KafkaProducer,
        bootstrap_servers=config.bootstrap_servers,
    )
    mongo = providers.Singleton(
        MongoDBClient,
        db_name=config.mongo.db_name,
        host=config.mongo.host,
        collection_name=config.mongo.collection,
        port=config.mongo.port,
        user=config.mongo.user,
        password=config.mongo.password,
    )
    pooler = providers.Singleton(Pooler)
    redis = providers.Singleton(MyRedis, config=config.redis)
    consumer = providers.Singleton(Consumer, config.kafka_config)
    prometheus = providers.Singleton(
        Prometheus, addr=config.prometheus.addr, port=config.prometheus.port
    )
    data_processor = providers.Singleton(
        KafkaDataProcessor,
        consumer=consumer,
        producer=producer,
        pooler=pooler,
        redis=redis,
        mongo=mongo,
        prometheus=prometheus,
    )
