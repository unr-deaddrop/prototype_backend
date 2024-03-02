from celery import shared_task
import time

@shared_task
def task23(data):
    print('task23')
    print(data)
    time.sleep(5)
    # return Response(data={'key':'val'})
    return