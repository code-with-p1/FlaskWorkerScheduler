import time
from rq import get_current_job

def counter_program():
    for i in range(1,1000):
        job = get_current_job()
        job.meta['current_step'] = i
        job.meta['info'] = "Counter >> " + str(i)
        job.save_meta()
        print("Current Step >> ", i)
        time.sleep(1)