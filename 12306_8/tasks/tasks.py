# coding:utf-8

from celery import Celery, platforms

from utils.config import broker
from utils.redis_utils import RedisUtils


redis = RedisUtils()

# 设置参数为True才能允许celery用root运行
platforms.C_FORCE_ROOT = True

config={}

# 设置任务中间件
config['CELERY_BROKER_URL'] = broker

# 设置时间
config['CELERY_TIMEZONE']= 'Asia/Shanghai'

# 非常重要,有些情况下可以防止死锁
config['CELERYD_FORCE_EXECV'] = True

# 一般推荐使用Redis来保存执行结果, 如果不关心worker执行结果, 关闭缓存结果可以提高程序的执行速度
config['CELERY_IGNORE_RESULT'] = True

# 每个worker最多执行100个任务就会被销毁，可防止内存泄露 销毁后重新创建新的worker
config['CELERYD_MAX_TASKS_PER_CHILD'] = 100

# 并发worker数
config['CELERYD_CONCURRENCY'] = 2

# 创建celery对象
celery = Celery(
    'tasks'
)

# 更新celery对象的配置
celery.conf.update(config)


if __name__ == '__main__':

    celery.start()