from __future__ import absolute_import
from celery import shared_task
import time

@shared_task(bind=True)
def add(self, x, y):
    time.sleep(10)
    return x + y


@shared_task
def mul(x, y):
    time.sleep(10)
    return x * y


@shared_task
def xsum(numbers):
    time.sleep(10)
    return sum(numbers)


@shared_task
def recorrer(valor):
    i=0
    while i <= valor:
        print('i',i)
        i=i+1
        time.sleep(10)
    return 'Recorrio el valor '+str(valor)