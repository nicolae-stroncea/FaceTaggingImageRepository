from flask_script import Manager
from api import create_app
from rq import Connection, Worker
import redis
import os
# sets up the app
app = create_app()

manager = Manager(app)


@manager.command
def runserver():
    app.run(debug=True, host="0.0.0.0", port=5001)


@manager.command
def runworker():
    app.run(debug=False)

@manager.command
def run_redis_worker():
    redis_url = os.getenv("REDIS_URL")
    redis_connection = redis.from_url(redis_url)
    queues = os.getenv("QUEUES",['default'])
    if not isinstance(queues, list):
        queues = [queues]
    with Connection(redis_connection):
        worker = Worker(queues)
        worker.work()

if __name__ == "__main__":
    manager.run()
