# coding:utf-8
import requests, json
import tornado.gen
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from tasks import celery
from utils.config import TIME_OUT
from utils.redis_utils import RedisUtils
from utils.parse_price import parsePrice


@celery.task
@tornado.gen.coroutine
def task_price(param_dict):
    seat_types = '123469PMOF'
    r = RedisUtils()
    s = requests.session()

    username = param_dict['username']
    train_date = param_dict['train_date']
    train_no = param_dict['train_no']
    from_station_no = param_dict['from_station_no']
    to_station_no = param_dict['to_station_no']

    # 判断登陆过期
    redis_dict = r.getSessionDict(username)
    if redis_dict == {} or redis_dict.get('cookies', '') == '':
        result_dict = {'status': '3', 'desc': '登陆过期', 'result': '请重新登陆'}
        r.setSessionDict(username, result_dict)
        return

    headers = json.loads(redis_dict['headers'].replace("'", '"'))
    cookies = redis_dict['cookies']
    s.cookies.update(json.loads(cookies))  # 更新

    url = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPriceFL?train_no=%s&from_station_no=%s&to_station_no=%s&seat_types=%s&train_date=%s' % (train_no, from_station_no, to_station_no, seat_types, train_date)
    _ = s.get(url, headers=headers, verify=False, timeout=TIME_OUT)

    url = 'https://kyfw.12306.cn/otn/leftTicket/queryTicketPrice?train_no=%s&from_station_no=%s&to_station_no=%s&seat_types=%s&train_date=%s' % (train_no, from_station_no, to_station_no, seat_types, train_date)
    response = s.get(url, headers=headers, verify=False, timeout=TIME_OUT)
    # print '='*30
    # print response.content
    if json.loads(response.content)['status'] != True:
        r.setSessionDict(username, {'status': '2', 'desc': '票价查询失败', 'result': response.content})
        return
    # 解析列车票价信息
    price_dict = parsePrice(json.loads(response.content)['data'])
    # print price_dict
    cookies = json.dumps(s.cookies.get_dict())
    # 构造并返回redis
    result_dict = {
        "status": '1',
        "desc": "票价查询成功",
        "result": json.dumps(price_dict),
        "cookies": cookies,
    }
    r.setSessionDict(username, result_dict)  # True
    return