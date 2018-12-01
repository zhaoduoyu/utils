# coding:utf-8

seat_type_dict = {}
seat_type_dict['shangwuzuo'] = "9" # 商务座
seat_type_dict['tedengzuo'] = "P" # 特等座
seat_type_dict['yidengzuo'] = "M" # 一等做
seat_type_dict['erdengzuo'] = "O" # 二等座
seat_type_dict['gaojiruanwo'] = "6" # 高级软卧
seat_type_dict['dongwo'] = "F" # 动卧
seat_type_dict['ruanwo'] = "4" # 软卧
seat_type_dict['yingwo'] = "3" # 硬卧
seat_type_dict['ruanzuo'] = "2" # 软座
seat_type_dict['yingzuo'] = "1" # 硬座
seat_type_dict['wuzuo'] = "1" # 无座

seat_list = [
    "erdengzuo",  # 二等座
    "yingwo",  # 硬卧
    "yingzuo",  # 硬座
    "wuzuo",  # 无座
    "ruanwo",  # 软卧
    "ruanzuo",  # 软座
    "dongwo",  # 动卧
    "yidengzuo",  # 一等座
    "gaojiruanwo",  # 高级软座
    "shangwuzuo",  # 商务座
    "tedengzuo",  # 特等座
]


if __name__ == '__main__':

    seat_type_pinyin = 'er'
    seat_pinyin = [seat_pinyin for seat_pinyin in seat_list] if seat_type_pinyin == '' else [seat_type_pinyin]
    print seat_pinyin

    if seat_type_pinyin not in seat_list and seat_type_pinyin != '':
        print 111