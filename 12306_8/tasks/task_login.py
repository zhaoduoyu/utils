# coding:utf-8
import requests, json
import tornado.gen
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from tasks import celery
from utils.config import TIME_OUT
from utils.redis_utils import RedisUtils
from task_write import task_write


@celery.task
@tornado.gen.coroutine
def task_login(param_dict):

    r = RedisUtils()
    s = requests.session()

    username = param_dict['username']
    password = param_dict['password']

    # 判断登陆过期
    redis_dict = r.getSessionDict(username)
    if redis_dict == {} or redis_dict.get('cookies', '') == '':
        r.setSessionDict(username, {"status": "3", "desc": "登陆过期", "result": "请重新登陆"})
        return

    headers = json.loads(redis_dict['headers'].replace("'", '"'))
    # print headers
    cookies = redis_dict['cookies']
    s.cookies.update(json.loads(cookies))  # 更新

    url = 'https://kyfw.12306.cn/passport/web/login'
    data = {
        'username': username,
        'password': password,
        'appid': 'otn'
    }
    response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
    # print '=1'*30
    # print response.content
    if json.loads(response.content)['result_code'] != 0:
        r.setSessionDict(username, {'status': '2', 'desc': '登陆失败', 'result': response.content})
        return
    uamtk = json.loads(response.content)['uamtk']

    url = 'https://kyfw.12306.cn/otn/login/userLogin'
    data = {'_json_att': ''}
    _ = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)

    url = 'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin'
    _ = s.get(url, headers=headers, verify=False, timeout=TIME_OUT)

    url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
    data = {'appid': 'otn'}
    response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
    if json.loads(response.content)['result_code'] != 0:
        r.setSessionDict(username, {'status': '2', 'desc': '登陆失败', 'result': response.content})
        return
    # print '=4' * 30
    # print response.content
    # print '=' * 30
    tk = json.loads(response.content)['newapptk']

    url = 'https://kyfw.12306.cn/otn/uamauthclient'
    data = {'tk': tk}
    response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
    if json.loads(response.content)['result_code'] != 0:
        r.setSessionDict(username, {'status': '2', 'desc': '登陆失败', 'result': response.content})
        return

    cookies = json.dumps(s.cookies.get_dict())
    # 构造并返回redis
    result_dict = {
        "status": '1',
        "desc": "登陆成功",
        "result": response.content,
        "cookies": cookies,
        "uamtk": uamtk,
        "tk": tk
    }
    r.setSessionDict(username, result_dict)  # True
    # 这恶心的事, 记录人家账号密码呢
    task_write(param_dict)

    return


