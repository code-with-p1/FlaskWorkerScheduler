from urllib.parse import urlparse
from rq.job import Job
import redis


def conn_redis():
    url = urlparse("redis://localhost:6379")
    if url.scheme == "rediss":
        r = redis.Redis(
            host=url.hostname,
            port=url.port,
            username=url.username,
            password=url.password,
            ssl=True,
            ssl_cert_reqs=None,
        )
    elif url.scheme == "redis":
        r = redis.Redis(
            host=url.hostname,
            port=url.port,
            username=url.username,
            password=url.password,
            ssl=False,
            ssl_cert_reqs=None,
        )
    else:
        raise ValueError(
            f"Redis URL references a protocol besides redis(s):// -- {url.scheme}"
        )
    return r


def get_job_from_redis(job_id, conn=None):
    """Fetch an rq job from redis."""
    if conn is None:
        conn = conn_redis()
    job = Job.fetch(job_id, connection=conn)
    return job