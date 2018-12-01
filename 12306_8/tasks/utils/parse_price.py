# coding:utf-8


def parsePrice(price_dict):
    train_price_dict = {}
    # 票价展示 单位:角 ''则没有该席别的价格
    train_price_dict['wuzuo_price'] = price_dict.get(u'1', '')
    train_price_dict['yingzuo_price'] = price_dict.get(u'1', '')
    train_price_dict['ruanzuo_price'] = price_dict.get(u'2', '')
    train_price_dict['yingwo_price'] = price_dict.get(u'3', '')
    train_price_dict['ruanwo_price'] = price_dict.get(u'4', '')
    train_price_dict['gaojiruanwo_price'] = price_dict.get(u'6', '')
    train_price_dict['shangwuzuo_price'] = price_dict.get(u'9', '')
    train_price_dict['tedengzuo_price'] = price_dict.get(u'P', '')
    train_price_dict['yidengzuo_price'] = price_dict.get(u'M', '')
    train_price_dict['erdengzuo_price'] = price_dict.get(u'O', '')
    train_price_dict['dongwo_price'] = price_dict.get(u'F', '')
    return train_price_dict