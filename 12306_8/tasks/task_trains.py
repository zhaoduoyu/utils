# coding:utf-8
import requests, json
import tornado.gen
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from tasks import celery
from utils.config import TIME_OUT
from utils.redis_utils import RedisUtils
from utils.stations import stations_long_str
from utils.parse_trains_infos import parseTrainsInfos


@celery.task
@tornado.gen.coroutine
def task_trains(param_dict):

    r = RedisUtils()
    s = requests.session()

    username = param_dict['username']
    from_station = param_dict['from_station'].encode('utf-8')
    to_station = param_dict['to_station'].encode('utf-8')
    train_date = param_dict['train_date'].encode('utf-8')

    # 判断登陆过期
    redis_dict = r.getSessionDict(username)
    if redis_dict == {} or redis_dict.get('cookies', '') == '':
        r.setSessionDict(username, {'status': '3', 'desc': '登陆过期', 'result': '请重新登陆'})
        return

    headers = json.loads(redis_dict['headers'].replace("'", '"'))
    # print headers
    cookies = redis_dict['cookies']
    s.cookies.update(json.loads(cookies))  # 更新

    # 获取{城市(车站):编码, ...} 键值对
    stations = {}
    for station in stations_long_str.split('@'):
        if not station: continue
        stations[station.split('|')[1]] = station.split('|')[2]
    # 获取城市(车站)编码
    from_station_code = stations.get(from_station, '')
    to_station_code = stations.get(to_station, '')

    url = 'https://kyfw.12306.cn/otn/login/checkUser'
    data = {'_json_att': ''}
    response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
    # print '=1'*30
    # print response.content
    if json.loads(response.content)['status'] != True:
        r.setSessionDict(username, {'status': '3', 'desc': json.loads(response.content)['messages'][0], 'result': response.content})
        return

    url = 'https://kyfw.12306.cn/otn/leftTicket/log?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' % (train_date, from_station_code, to_station_code)
    response = s.get(url, headers=headers, verify=False, timeout=TIME_OUT)
    # print '=2'*30
    # print response.content
    if json.loads(response.content)['status'] != True:
        r.setSessionDict(username, {'status': '2', 'desc': '列车查询失败, 12306抽风了', 'result': response.content})
        return

    url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' % (train_date, from_station_code, to_station_code)
    response = s.get(url, headers=headers, verify=False, timeout=TIME_OUT)
    # print '=3'*30
    # print response.content
    if json.loads(response.content)['status'] != True:
        r.setSessionDict(username, {'status': '2', 'desc': '列车查询失败, 12306抽风了', 'result': response.content})
        return

    trains_list = parseTrainsInfos(json.loads(response.content)['data']['result'])
    # print trains_list
    cookies = json.dumps(s.cookies.get_dict())
    # 构造并返回redis
    result_dict = {
        "status": '1',
        "desc": "列车查询成功",
        "result": json.dumps({'trains_list':trains_list}),
        "cookies": cookies,
    }
    r.setSessionDict(username, result_dict)  # True
    return
