# coding:utf-8
import requests, json
import tornado.gen
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from tasks import celery
from utils.config import TIME_OUT
from utils.redis_utils import RedisUtils


@celery.task
@tornado.gen.coroutine
def task_bcode(param_dict):

    r = RedisUtils()
    s = requests.session()

    username = param_dict['username']
    bcode = param_dict['bcode']

    # 判断登陆过期
    redis_dict = r.getSessionDict(username)
    if redis_dict == {} or redis_dict.get('cookies', '') == '':
        r.setSessionDict(username, {'status': '3', 'desc': '登陆过期', 'result': '请重新登陆'})
        return

    headers = json.loads(redis_dict['headers'].replace("'", '"'))
    # print headers
    cookies = redis_dict['cookies']
    s.cookies.update(json.loads(cookies))  # 更新

    # 根据bcode参数构造12306所需参数 answer
    img_xy_list = ['35,35', '105,35', '175,35', '245,35', '35,105', '105,105', '175,105', '245,105']
    answer = ''
    for img_code in bcode.split(','): answer = answer + img_xy_list[int(img_code) - 1] + ','
    # print answer[:-1]

    url = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
    data = {'login_site': 'E', 'rand': 'sjrand', 'answer': answer[:-1]}
    response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
    # 判断成功
    if json.loads(response.content)['result_code'] == '4':
        cookies = json.dumps(s.cookies.get_dict())
        # 构造并返回redis
        result_dict = {
            "status": '1',
            "desc": "验证成功",
            "result": response.content,
            "cookies": cookies,
        }
        r.setSessionDict(username, result_dict)  # True
        return

    r.setSessionDict(username, {'status': '2', 'desc': '验证失败', 'result': response.content})
    return
