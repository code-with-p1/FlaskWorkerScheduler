from rq import Queue, Connection
from rq.worker import HerokuWorker as Worker
from redis_util import conn_redis

# Workers
listen = ['high', 'default', 'low']

# Connect To Redis
conn = conn_redis()

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work(with_scheduler=True)
