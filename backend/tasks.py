from celery import shared_task
import time

@shared_task
def task23():
    print('task23')
    time.sleep(5)
    # return Response(data={'key':'val'})
    return