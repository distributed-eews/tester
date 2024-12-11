import redis
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


class RedisSingleton:
    _instance = None

    def __new__(cls, db=0):
        if cls._instance is None:
            cls._instance = super(RedisSingleton, cls).__new__(cls)
            cls._instance.r = redis.Redis(
                host=REDIS_HOST,
                port=int(REDIS_PORT),
                db=db,
                decode_responses=True,
                password=REDIS_PASSWORD,
            )
        return cls._instance
