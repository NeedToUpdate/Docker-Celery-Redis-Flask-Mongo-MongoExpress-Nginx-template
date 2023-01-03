import time
from celery import Celery
from celery.utils.log import get_task_logger
import requests

logger = get_task_logger(__name__)

app = Celery('tasks', broker='redis://redis:6379/0',
             backend='redis://redis:6379/0')


@app.task()
def get_image(search_data):
    res = requests.get(f'https://commons.wikimedia.org/w/api.php?action=query&format=json&uselang=en&generator=search&gsrsearch=filetype%3Abitmap|drawing%20-fileres%3A0%20{"%20".join(search_data["name"].split(" "))}&prop=info|imageinfo|entityterms&inprop=url&gsrnamespace=6&iiprop=url|size|mime', headers={
                       'user-agent': 'Just getting some images of cars. email: contact@icandoathing.com'})
    images = res.json().get('query')
    if not images:
        return {
            'full_url': '',
            'image_url': '',
            '_id': search_data['_id'],
            'rel_id': search_data['rel_id']
        }
    first = list(images.get('pages').values())[0]
    if first:
        return {
            'full_url': first['fullurl'],
            'image_url': first['imageinfo'][0]['url'],
            '_id': search_data['_id'],
            'rel_id': search_data['rel_id']
        }
    return {
        'full_url': '',
        'image_url': '',
        '_id': search_data['_id'],
        'rel_id': search_data['rel_id']
    }
