import time
from celery import Celery
from celery.utils.log import get_task_logger
import requests

logger = get_task_logger(__name__)

app = Celery('tasks', broker='redis://redis:6379/0',
             backend='redis://redis:6379/0')


@app.task()
def get_data(id):
    logger.info(f'Getting Pokemon #{id}')
    res = requests.get(f'https://pokeapi.co/api/v2/pokemon/{id}')
    json = res.json()
    return json
