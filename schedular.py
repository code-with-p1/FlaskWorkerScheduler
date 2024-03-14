import rq_scheduler as rqs
from redis_util import conn_redis

# Connect To Redis
conn = conn_redis()

if __name__ == '__main__':
    scheduler = rqs.Scheduler(connection=conn)
    scheduler.run()