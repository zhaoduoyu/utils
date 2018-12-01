# coding:utf-8

import urllib


def parseTrainsInfos(trains_list):
    """
    解析列车信息列表, 返回列车信息列表
    :param trains_list:
    :return:
    """
    trains_infos_list = []

    if trains_list == []:
        return []

    for train_info in trains_list:
        train_info_list = train_info.split('|')
        train_info_dict = {}
        # 构造列车信息
        train_info_dict['secretStr'] = urllib.unquote(train_info_list[0])  # secretStr ;为''时无法购买车票
        # train_info_list[1]  预定/列车停运
        train_info_dict['train_no'] = urllib.unquote(train_info_list[2])  # train_no
        train_info_dict['stationTrainCode'] = urllib.unquote(train_info_list[3])  # stationTrainCode 即车次 # 展示
        train_info_dict['start_station'] = urllib.unquote(train_info_list[4])  # 始发站 # 展示
        train_info_dict['end_station'] = urllib.unquote(train_info_list[5])  # 终点站 # 展示
        train_info_dict['from_station'] = urllib.unquote(train_info_list[6])  # 出发站 # 展示
        train_info_dict['to_station'] = urllib.unquote(train_info_list[7])  # 到达站 # 展示
        train_info_dict['from_time'] = urllib.unquote(train_info_list[8])  # 出发时间 # 展示
        train_info_dict['to_time'] = urllib.unquote(train_info_list[9])  # 到达时间 # 展示
        train_info_dict['use_time'] = urllib.unquote(train_info_list[10])  # 时长 # 展示
        train_info_dict['buy_able'] = urllib.unquote(train_info_list[11])  # 能否购买 Y 可以购买 N 不可以购买 IS_TIME_NOT_BUY 停运 # 展示
        train_info_dict['leftTicket'] = urllib.unquote(train_info_list[12])  # leftTicket
        train_info_dict['start_time'] = urllib.unquote(train_info_list[13])  # 车次始发日期 # 展示
        train_info_dict['train_location'] = urllib.unquote(train_info_list[15])  # train_location 不知道是啥??
        train_info_dict['from_station_no'] = urllib.unquote(train_info_list[16])  # 出发站编号
        train_info_dict['to_station_no'] = urllib.unquote(train_info_list[17])  # 到达站编号
        # 14,18,19,20,27,34,35未知
        train_info_dict['gaojiruanwo'] = urllib.unquote(train_info_list[21])  # 高级软卧 # 展示
        train_info_dict['qita'] = urllib.unquote(train_info_list[22])  # 其他 # 展示
        train_info_dict['ruanwo'] = urllib.unquote(train_info_list[23])  # 软卧 # 展示
        train_info_dict['ruanzuo'] = urllib.unquote(train_info_list[24])  # 软座 # 展示
        train_info_dict['tedengzuo'] = urllib.unquote(train_info_list[25])  # 特等座 # 展示
        train_info_dict['wuzuo'] = urllib.unquote(train_info_list[26])  # 无座 # 展示
        train_info_dict['yingwo'] = urllib.unquote(train_info_list[28])  # 硬卧 # 展示
        train_info_dict['yingzuo'] = urllib.unquote(train_info_list[29])  # 硬座 # 展示
        train_info_dict['erdengzuo'] = urllib.unquote(train_info_list[30])  # 二等座 # 展示
        train_info_dict['yidengzuo'] = urllib.unquote(train_info_list[31])  # 一等座 # 展示
        train_info_dict['shangwuzuo'] = urllib.unquote(train_info_list[32])  # 商务座 # 展示
        train_info_dict['dongwo'] = urllib.unquote(train_info_list[33])  # 动卧 # 展示

        # 获取票价信息 ### 频繁访问限制
        # price_dict = getTicketPrice(
        #     cookies_json,
        #     train_date,
        #     seat_types='123469PMOF',
        #     train_no = train_info_dict['train_no'],
        #     from_station_no = train_info_dict['from_station_no'],
        #     to_station_no = train_info_dict['to_station_no']
        # )
        # print '-'*30
        # print train_info_dict['stationTrainCode']
        # print price_dict
        # 票价展示 单位:角 ''则没有该席别
        # train_info_dict['wuzuo_price'] = price_dict.get(u'1', '')
        # train_info_dict['yingzuo_price'] = price_dict.get(u'1', '')
        # train_info_dict['ruanzuo_price'] = price_dict.get(u'2', '')
        # train_info_dict['yingwo_price'] = price_dict.get(u'3', '')
        # train_info_dict['ruanwo_price'] = price_dict.get(u'4', '')
        # train_info_dict['gaojiruanwo_price'] = price_dict.get(u'6', '')
        # train_info_dict['shangwuzuo_price'] = price_dict.get(u'9', '')
        # train_info_dict['tedengzuo_price'] = price_dict.get(u'P', '')
        # train_info_dict['yidengzuo_price'] = price_dict.get(u'M', '')
        # train_info_dict['erdengzuo_price'] = price_dict.get(u'O', '')
        # train_info_dict['dongwo_price'] = price_dict.get(u'F', '')

        trains_infos_list.append(train_info_dict)

    return trains_infos_list
