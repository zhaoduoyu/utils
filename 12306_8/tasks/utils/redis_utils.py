# coding:utf-8

# import rediscluster
import redis
from config import HOST, PORT


class RedisUtils():

    def __init__(self):

        # host_list = HOST.split(",")
        # port_list = PORT.split(",")
        # redis_nodes = []
        # for host in host_list:
        #     for port in port_list:
        #         redis_nodes.append({'host': host, 'port': port})
        # self.cluster = rediscluster.StrictRedisCluster(startup_nodes=redis_nodes, max_connections=32)

        self.cluster = redis.StrictRedis(host=HOST, port=PORT)
        self.task_name = '12306_session:'


    # 写入redis; tasks调用的方法
    def setSessionDict(self, username, result_dict):
        res = self.cluster.hmset(self.task_name + username, result_dict)  # 成功返回true
        self.cluster.expire(self.task_name + username, 1600)  # 设置过期时间 单位:秒
        return res


    # 读取redis; tasks调用的方法
    def getSessionDict(self, username):
        return self.cluster.hgetall(self.task_name + username)



if __name__ == '__main__':

    r = RedisUtils()
    print r.cluster.keys('12306_*')
    for i in r.cluster.keys('12306_*'):
        print r.cluster.delete(i)
    print r.cluster.keys('12306_*')
    print r.cluster.delete('hahaha')

    print r.getSessionDict('12306'), 222