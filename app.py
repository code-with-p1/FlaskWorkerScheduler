from flask import Flask,jsonify
from redis import Redis
import rq
import flask
from datetime import datetime, timedelta
from rq.job import Job
from rq_scheduler import Scheduler
from programs import counter_program
from rq.command import send_stop_job_command
from redis_util import conn_redis, get_job_from_redis

app = Flask(__name__)

# Created Redis Connection
redis_conn = conn_redis()

@app.route('/')
def start_queue():
    q = rq.Queue(connection=redis_conn, default_timeout=3600)
    job = q.enqueue(counter_program)
    job.meta['current_step'] = None
    job.save_meta()
    result = {}
    result['job_id'] = job.id
    return jsonify(result)

@app.route('/schedule')
def schedule_job():
    queue = "default"
    enqueue_datetime = datetime.now()
    enqueue_datetime = enqueue_datetime + timedelta(minutes=1)

    q = rq.Queue(queue=queue, connection=redis_conn, default_timeout=3600)
    sched = Scheduler(queue=q, connection=q.connection)

    job = sched.enqueue_in(
        timedelta(minutes=1), counter_program
    )

    print('Job >>' , job)
    exit()
    
    job.meta['current_step'] = None
    job.save_meta()
    result = {}
    result['job_id'] = job.id
    return jsonify(result)

@app.route('/job/status/<id>')
def get_job_status(id):
    job = Job.fetch(id, connection=redis_conn)
    result = {}
    result['job_status'] = job.get_status()
    result['current_step'] = job.meta['current_step']
    return jsonify(result)

@app.route('/job/cancel/<job_id>')
def cancel_job(job_id):

    try:
        job = get_job_from_redis(job_id, redis_conn)
    except rq.exceptions.NoSuchJobError:
        flask.abort(404, "Invalid job id")

    if job.is_started:
        try:
            send_stop_job_command(redis_conn, job_id)
            result = {"result": "success", "detail": f"Stopped running job {job_id}"}
            return flask.jsonify(result)
        except:
            result = {
                "result": "failure",
                "detail": (
                    f"Unable to stop running job {job_id}. "
                    "Job may have already completed, or id may be invalid"
                ),
            }
            return flask.jsonify(result)
    elif job.is_queued:
        try:
            job.cancel()
            job.set_status("canceled")
            result = {"result": "success", "detail": f"Cancelled queued job {job_id}"}
            return flask.jsonify(result)
        except:
            result = {
                "result": "failure",
                "detail": (
                    f"Unable to cancel queued job {job_id}. "
                    "Job may no longer be queued, or id may be invalid"
                ),
            }
            return flask.jsonify(result)
    else:
        result = {
            "result": "failure",
            "detail": "Job is not cancelable. It is probably already finished.",
        }
        return flask.jsonify(result)

if __name__ == '__main__':
   app.run(port=9000)