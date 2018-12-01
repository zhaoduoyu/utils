# coding:utf-8

import time
import tornado.gen
from tasks import celery


@celery.task
@tornado.gen.coroutine
def task_sleep(i):
    time.sleep(i)
    return

