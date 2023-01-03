from bson.json_util import dumps
import random
import time
from flask import Flask
from celery import Celery
from pymongo import MongoClient
from bson.objectid import ObjectId
from queue import Queue
import threading
import os

MAX_PAGE = 305

# connect to all services
app = Flask(__name__)
celery_worker = Celery(
    'simple_worker', broker='redis://redis:6379/0', backend='redis://redis:6379/0')
client = MongoClient(
    host='mongodb', port=27017, username=os.environ['MONGODB_USERNAME'], password=os.environ['MONGODB_PASSWORD'])

db = client['new_db']


# wrapper for Threads, since we need to stop them, this is the way to get out of their while loops
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


# used to answer the /status route
is_running = False


@app.route('/')
def index():
    return '<a href="/start">start</a>' if not is_running else '<a href="/stop">stop</a>'


images_to_get = Queue()


@app.route('/runstartscript')
def run_start_script():
    # clear queue
    while not images_to_get.empty():
        images_to_get.get()
    for car in db['car_names'].find({'done': False}):
        images_to_get.put(car)
    return 'ok'


# one method fills up the queue, other method consumes it
tasks = Queue()


def get_next_page():
    global tasks
    seconds_bw_requests = 0.01
    while not threading.current_thread().stopped() and not images_to_get.empty():
        start = time.time()
        search_data = images_to_get.get()
        search_data['_id'] = str(search_data['_id'])
        search_data['rel_id'] = str(search_data['rel_id'])
        task = celery_worker.send_task(
            'tasks.get_image', kwargs={'search_data': search_data})
        tasks.put(task.id)
        end = time.time()
        remain = start + seconds_bw_requests - end
        if remain > 0:
            time.sleep(remain)


def check_results():
    global tasks
    seconds_bw_checks = 1
    while not threading.current_thread().stopped():
        start = time.time()
        while not tasks.empty() and threading.current_thread().stopped():
            task = tasks.get()
            task_res = celery_worker.AsyncResult(task, app=celery_worker).get()
            if task_res is not None:
                rel_id = task_res['rel_id']
                db['cars'].update_one({'_id': ObjectId(rel_id)}, {'$set': {
                                      'image_url': task_res['image_url'], 'full_url': task_res['full_url']}})
                db['car_names'].update_one({'_id': ObjectId(task_res['_id'])}, {
                                           "$set": {'done': True}})
            else:
                tasks.put(task)
        end = time.time()
        remain = start + seconds_bw_checks - end
        if remain > 0:
            time.sleep(remain)


threads = []


@app.route('/start')
def start_requests():
    global threads
    global is_running
    run_start_script()
    thread = StoppableThread(target=get_next_page)
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


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    run_start_script()
    app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
