# coding:utf-8
import requests, json, re, time, random
import tornado.gen
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from tasks import celery
from utils.config import TIME_OUT
from utils.redis_utils import RedisUtils
from utils.seat_type import seat_list, seat_type_dict
from utils.parse_date import parseDate
from task_sleep import task_sleep


@celery.task
@tornado.gen.coroutine
def task_buy(param_dict):

    r = RedisUtils()
    s = requests.session()

    username = param_dict['username']
    train_date = param_dict['train_date'].encode('utf-8')
    from_station = param_dict['from_station'].encode('utf-8')
    to_station = param_dict['to_station'].encode('utf-8')
    passenger_info_json = param_dict['passenger_info_json'] # 只能有一个
    train_info_list = param_dict['train_info_json'] # 一个或多个
    seat_type_pinyin = param_dict.get('seat_type_pinyin', '') # 一个或空

    # print type(passenger_info_json), type(train_info_list)
    # 判断登陆过期
    redis_dict = r.getSessionDict(username)
    if redis_dict == {} or redis_dict.get('cookies', '') == '':
        result_dict = {'status': '3', 'desc': '登陆过期', 'result': '请重新登陆'}
        r.setSessionDict(username, result_dict)
        return
    # 判断参数
    if seat_type_pinyin not in seat_list and seat_type_pinyin != '':
        result_dict = {'status': '2', 'desc': '参数异常', 'result': 'your seat_type_pinyin is %s'%seat_type_pinyin}
        r.setSessionDict(username, result_dict)
        return

    headers = json.loads(redis_dict['headers'].replace("'", '"'))
    # print headers
    cookies = redis_dict['cookies']
    s.cookies.update(json.loads(cookies))  # 更新

    for train_info_dict in train_info_list:
        seat_pinyin = [seat_pinyin for seat_pinyin in seat_list] if seat_type_pinyin == '' else [seat_type_pinyin]
        for seat in seat_pinyin:
            if train_info_dict[seat] != '' and train_info_dict[seat] != '无':
                # 席别
                seat_type = seat_type_dict[seat]
                # print seat_type_pinyin, seat_type
                # 乘客信息
                passenger_info_dict = passenger_info_json[0]
                passengerTicketStr = '%s,0,1,%s,%s,%s,%s,N' % (
                seat_type, passenger_info_dict['passenger_name'],
                passenger_info_dict['passenger_id_type_code'],
                passenger_info_dict['passenger_id_no'],
                passenger_info_dict['passenger_mobile_no'])

                oldPassengerStr = '%s,%s,%s,1_' % (
                passenger_info_dict['passenger_name'],
                passenger_info_dict['passenger_id_type_code'],
                passenger_info_dict['passenger_id_no'])

                # 列车信息
                secretStr = train_info_dict['secretStr']
                leftTicket = train_info_dict['leftTicket']
                train_location = train_info_dict['train_location']

                # 验证登陆状态
                url = 'https://kyfw.12306.cn/otn/login/checkUser'
                data = {'_json_att': ''}
                response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
                # print '=0' * 30
                # print response.content
                if json.loads(response.content)['status'] != True:
                    r.setSessionDict(username, {'status': '3', 'desc': json.loads(response.content)['messages'][0],
                                                'result': response.content})
                    return

                # 准备下单
                url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
                data = {
                    'secretStr': secretStr,
                    'train_date': train_date,
                    'back_train_date': train_date,
                    'tour_flag': 'dc',  # dc 单程 wf 往返
                    'purpose_codes': 'ADULT',  # 成人
                    'query_from_station_name': from_station,
                    'query_to_station_name': to_station,
                    'undefined': ''
                }
                response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
                # print '=1' * 30
                # print response.content
                try:
                    if json.loads(response.content)['status'] != True:
                        continue
                except:
                    result_dict = {'status': '3', 'desc': '登陆过期', 'result': '请重新登陆'}
                    r.setSessionDict(username, result_dict)
                    return

                # 订单初始化 获取 repeat_submit_token, key_check_isChange
                try:
                    url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
                    data = {'_json_att': ''}
                    response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
                    repeat_submit_token = re.search(r"var globalRepeatSubmitToken = '([a-z0-9]+)';", response.content).group(1)
                    key_check_isChange = re.search("'key_check_isChange':'([A-Z0-9]+)'", response.content).group(1)
                    # print '获取repeat_submit_token, key_check_isChange'
                    # print repeat_submit_token
                    # print key_check_isChange
                except:
                    continue

                # 下单-订单检查
                url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
                data = {
                    'cancel_flag': '2',  # 未知
                    'bed_level_order_num': '000000000000000000000000000000',  # 未知
                    'passengerTicketStr': passengerTicketStr.encode('utf-8'),
                    'oldPassengerStr': oldPassengerStr.encode('utf-8'),
                    'tour_flag': 'dc',  # 单程
                    'randCode': '',
                    '_json_att': '',
                    'REPEAT_SUBMIT_TOKEN': repeat_submit_token
                }
                response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
                # print '订单检查:', response.content
                if json.loads(response.content)['data']['submitStatus'] == False:
                    continue
                if json.loads(response.content)['status'] == False:
                    continue

                # 查询排队情况
                url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
                data = {
                    'train_date': parseDate(train_date),  # Fri Nov 24 2017 00:00:00 GMT+0800 (中国标准时间)
                    'train_no': train_info_dict['train_no'],  # 6c0000G31205
                    'stationTrainCode': train_info_dict['stationTrainCode'],  # G312
                    'seatType': seat_type,  # 席别
                    'fromStationTelecode': train_info_dict['from_station'],  # one_train[6]
                    'toStationTelecode': train_info_dict['to_station'],  # ? one_train[7]
                    'leftTicket': train_info_dict['leftTicket'],  # one_train[12]
                    'purpose_codes': '00',
                    'train_location': train_info_dict['train_location'],  # one_train[15]
                    '_json_att': '',
                    'REPEAT_SUBMIT_TOKEN': repeat_submit_token
                }
                response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
                # print '查询排队情况:', response.content
                if json.loads(response.content)['status'] == False:
                    continue

                # 提交订单排队
                for i in xrange(3):
                    url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
                    data = {
                        'passengerTicketStr': passengerTicketStr.encode('utf-8'),
                        'oldPassengerStr': oldPassengerStr.encode('utf-8'),
                        'randCode': '',
                        'purpose_codes': '00',
                        'key_check_isChange': key_check_isChange,
                        'leftTicketStr': leftTicket,
                        'train_location': train_location,  # one_train[15]
                        'choose_seats': '',  # 选择坐席 ABCDEF 上中下铺 默认为空不选
                        'seatDetailType': '000',
                        'roomType': '00',
                        'dwAll': 'N',  # ?
                        '_json_att': '',
                        'REPEAT_SUBMIT_TOKEN': repeat_submit_token
                    }
                    response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
                    # print '提交订单排队:', response.content

                    if json.loads(response.content)['status'] != True:
                        break
                    elif json.loads(response.content)['data']['submitStatus'] == False:
                        continue
                    else:
                        break
                if json.loads(response.content)['status'] == False:
                    continue
                if json.loads(response.content)['data']['submitStatus'] == False:
                    continue

                # 获取订单流水号
                orderSequence_no = ''
                for i in range(3):
                    timestamp = str(int(time.time() * 1000))
                    url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=%s&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=%s' % (timestamp, repeat_submit_token)
                    response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
                    # print '获取订单流水号:', response.content

                    try:
                        orderSequence_no = json.loads(response.content)['data']['orderId']
                    except:
                        continue
                    waitTime = json.loads(response.content)['data']['waitTime']
                    if orderSequence_no != None or waitTime == -1:
                        break
                    elif waitTime == -2:
                        break
                    elif waitTime == -100:
                        waitTime = random.randint(3, 8)
                        task_sleep(waitTime)
                    else:
                        task_sleep(waitTime)
                if json.loads(response.content)['status'] == False:
                    _ = yield tornado.gen.Task(task_sleep, 5)
                    continue

                # 获取订票结果
                url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
                data = {
                    'orderSequence_no': orderSequence_no,
                    '_json_att': '',
                    'REPEAT_SUBMIT_TOKEN': repeat_submit_token
                }
                response = s.post(url, data=data, headers=headers, verify=False, timeout=TIME_OUT)
                # print '订票结果: ', response.content
                if json.loads(response.content)['status'] == True and \
                json.loads(response.content)['data']['submitStatus'] == True:
                    cookies = json.dumps(s.cookies.get_dict())
                    # 构造并返回redis
                    result_dict = {
                        "status": '1',
                        "desc": "购票成功",
                        "result": response.content,
                        "cookies": cookies,
                    }
                    r.setSessionDict(username, result_dict)  # True
                    return

    # 构造并返回redis
    result_dict = {
        "status": '2',
        "desc": "购票失败",
        "result": "请五秒后尝试"
    }
    r.setSessionDict(username, result_dict)  # True
    return



