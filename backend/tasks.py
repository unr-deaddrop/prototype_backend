from celery import shared_task
import time
import logging
logger = logging.getLogger(__name__)

@shared_task
def task23(data):
    # print('task23')
    logger.info('task234')
    print(data)
    time.sleep(5)
    # return Response(data={'key':'val'})
    return