# coding:utf-8
import requests, json, random, base64
import tornado.gen
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from tasks import celery
from utils.config import headers, TIME_OUT
from utils.redis_utils import RedisUtils


@celery.task
@tornado.gen.coroutine
def task_img(param_dict):

    r = RedisUtils()

    username = param_dict['username']

    s = requests.session()
    header = headers

    # 获取验证图片
    url = "https://kyfw.12306.cn/otn/login/init"
    s.get(url, headers=header, verify=False, timeout=TIME_OUT)
    url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&%.16f" % random.random()
    response = s.get(url, headers=header, verify=False, timeout=TIME_OUT)

    # 把验证码图片保存到本地
    # img_file_path_str = "./static/" + username + ".jpeg"
    # img_file_path_str = "./static/" + "test" + ".jpeg"
    # with open(img_file_path_str, "wb") as f: f.write(response.content)

    # 获取验证图片的base64编码
    img_base64_str = base64.b64encode(response.content)
    # 获取session.cookies
    """
        json.dumps(session.cookies.get_dict())) # 保存
        session.cookies.update(json.loads(f.read())) # 读取
    """
    cookies = json.dumps(s.cookies.get_dict())

    # 构造并返回redis
    result_dict = {
        "status": '1',
        "desc": "获取验证图片成功",
        "result": {"img_base64_str": img_base64_str},
        "cookies": cookies,
        "username": username,
        "headers": header,
    }
    r.setSessionDict(username, result_dict)  # True
    # print 111
    return

