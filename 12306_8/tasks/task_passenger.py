# coding:utf-8
import requests, json
import tornado.gen
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from tasks import celery
from utils.config import TIME_OUT
from utils.redis_utils import RedisUtils
from utils.parse_passenger import parsePassenger


@celery.task
@tornado.gen.coroutine
def task_passenger(param_dict):

    r = RedisUtils()
    s = requests.session()

    username = param_dict['username']

    # 判断登陆过期
    redis_dict = r.getSessionDict(username)
    if redis_dict == {} or redis_dict.get('cookies', '') == '':
        result_dict = {'status': '3', 'desc': '登陆过期', 'result': '请重新登陆'}
        r.setSessionDict(username, result_dict)
        return

    headers = json.loads(redis_dict['headers'].replace("'", '"'))
    # print headers
    cookies = redis_dict['cookies']
    s.cookies.update(json.loads(cookies))  # 更新

    url = 'https://kyfw.12306.cn/otn/login/checkUser'
    data = {'_json_att': ''}
    response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
    # print '=1'*30
    # print response.content
    if json.loads(response.content)['status'] != True:
        r.setSessionDict(username, {'status': '3', 'desc': json.loads(response.content)['messages'][0], 'result': response.content})
        return

    url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
    data = {'_json_att': ''}
    response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
    # print '=2'*30
    # print response.content
    if json.loads(response.content)['status'] != True:
        r.setSessionDict(username, {'status': '3', 'desc': json.loads(response.content)['messages'][0], 'result': response.content})
        return

    # 解析并构造乘客信息列表
    passenger_list = parsePassenger(json.loads(response.content))
    cookies = json.dumps(s.cookies.get_dict())
    # 构造并返回redis
    result_dict = {
        "status": '1',
        "desc": "票价查询成功",
        "result": json.dumps({'passenger_list':passenger_list}),
        "cookies": cookies,
    }
    r.setSessionDict(username, result_dict)  # True
    return