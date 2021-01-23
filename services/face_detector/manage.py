from api.config import config
from rq import Connection, Worker
import redis
import os


def run_redis_worker():
    redis_url = os.getenv("REDIS_URL")
    redis_connection = redis.from_url(redis_url)
    env = os.getenv("FLASK_ENV")
    queues = config[env].QUEUES
    with Connection(redis_connection):
        worker = Worker(queues)
        worker.work()

if __name__ == "__main__":
    run_redis_worker()
