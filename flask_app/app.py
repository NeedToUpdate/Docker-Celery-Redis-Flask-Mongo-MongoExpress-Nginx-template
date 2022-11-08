from bson.json_util import dumps
import random
import time
from flask import Flask
from celery import Celery
from pymongo import MongoClient
from queue import Queue
import threading
import os
app = Flask(__name__)
celery_worker = Celery(
    'simple_worker', broker='redis://redis:6379/0', backend='redis://redis:6379/0')


client = MongoClient(
    host='mongodb', port=27017, username=os.environ['MONGODB_USERNAME'], password=os.environ['MONGODB_PASSWORD'])

db = client['new_db']


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


@app.route('/')
def index():
    return '<a href="/start">start</a>'


tasks = Queue()
is_running = False


def get_random_poke():
    global tasks
    seconds_bw_requests = 5
    while not threading.current_thread().stopped():
        start = time.time()
        id = random.randint(1, 950)
        task = celery_worker.send_task('tasks.get_data', kwargs={'id': id})
        tasks.put(task.id)
        end = time.time()
        remain = start + seconds_bw_requests - end
        if remain > 0:
            time.sleep(remain)
            

def check_results():
    global tasks
    seconds_bw_checks = 10
    while not threading.current_thread().stopped():
        start = time.time()
        while tasks.not_empty:
            task = tasks.get()
            task_res = celery_worker.AsyncResult(task, app=celery_worker).get()
            if task_res is not None:
                db['pokes'].insert_one(task_res)
        end = time.time()
        remain = start + seconds_bw_checks - end
        if remain > 0:
            time.sleep(remain)
   

threads = []


@app.route('/start')
def start_requests():
    global threads
    global is_running
    thread = StoppableThread(target=get_random_poke)
    checker = StoppableThread(target=check_results)
    threads.append(thread)
    threads.append(checker)
    thread.start()
    checker.start()

    return '<a href="/">Go Back</a>'


@app.route('/stop')
def stop_requests():
    global threads
    global is_running
    for thread in threads:
        thread.stop()
    threads = []
    is_running = False
    return '<a href="/">Go Back</a>'


@app.route('/status')
def get_status():
    return 'running' if is_running else 'stopped'


@app.route('/result/<task_id>')
def task_result(task_id):
    return celery_worker.AsyncResult(task_id).result


@app.route('/all_data')
def get_data():
    return dumps(db['pokes'].find({}))


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
