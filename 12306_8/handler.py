# coding:utf-8
import json, os, redis
import tornado.gen
import tornado.ioloop
import tornado.web

from tasks.utils.config import HOST, PORT
from tasks.task_img import task_img
from tasks.task_bcode import task_bcode
from tasks.task_login import task_login
from tasks.task_trains import task_trains
from tasks.task_price import task_price
from tasks.task_passenger import task_passenger
from tasks.task_buy import task_buy


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.cluster = redis.StrictRedis(host=HOST, port=PORT)
        self.task_name = '12306_session:'


    # 读取redis; tornado-handler调用的方法
    @tornado.gen.coroutine
    def getResult(self, username):
        val_list = self.cluster.hmget(self.task_name + username, 'status', 'desc', 'result')
        return {'status': val_list[0], 'desc': val_list[1], 'result': val_list[2]}


    @tornado.web.asynchronous # 长连接, self.finish()才关闭连接
    @tornado.gen.coroutine # 仅仅是声明:这是个异步函数
    def post(self, api_name): # api_name是自定义的url路径
        print '='*30
        print json.loads(self.request.body)
        username = json.loads(self.request.body).get("username", '')
        if username == '':
            result_dict = {"status": '2', "desc": '参数异常', "result": 'your username is: None'}
            self.finish(result_dict)
            return

        # 解析参数,并异步调用相应的celery异步方法
        param_dict = json.loads(self.request.body)
        # apk文件下载:正常都是扔给nginx
        if api_name == 'apk':
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=huochepiao.apk')
            with open('./static/huochepiao.apk', 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data: break
                    self.write(data)
            self.finish()
            return

        elif api_name == 'img':
            _ = yield tornado.gen.Task(task_img, param_dict)

        elif api_name == 'bcode':
            if json.loads(self.request.body).get('bcode', '') == '':
                self.finish({"status": '2', "desc": '参数异常', "result": 'your bcode is: None'})
                return
            _ = yield tornado.gen.Task(task_bcode, param_dict)

        elif api_name == 'login':
            if json.loads(self.request.body).get('password', '') == '':
                self.finish({"status": '2', "desc": '参数异常', "result": 'your password is: None'})
                return
            _ = yield tornado.gen.Task(task_login, param_dict)

        elif api_name == 'trains':
            if \
            json.loads(self.request.body).get('train_date', '') == '' or \
            json.loads(self.request.body).get('from_station', '') == '' or \
            json.loads(self.request.body).get('to_station', '') == '' :
                self.finish({"status": '2', "desc": '参数异常', "result": 'train_date or from_station or to_station is: None'})
                return
            _ = yield tornado.gen.Task(task_trains, param_dict)

        elif api_name == 'price':
            if \
            json.loads(self.request.body).get('train_date', '') == '' or \
            json.loads(self.request.body).get('train_no', '') == '' or \
            json.loads(self.request.body).get('from_station_no', '') == '' or \
            json.loads(self.request.body).get('to_station_no', '') == '' :
                self.finish({"status": '2', "desc": '参数异常', "result": 'train_no or from_station_no or to_station_no or train_date is: None'})
                return
            _ = yield tornado.gen.Task(task_price, param_dict)

        elif api_name == 'passenger':
            _ = yield tornado.gen.Task(task_passenger, param_dict)

        elif api_name == 'buy':
            if \
            json.loads(self.request.body).get('train_date', '') == '' or \
            json.loads(self.request.body).get('from_station', '') == '' or \
            json.loads(self.request.body).get('to_station', '') == '' or \
            json.loads(self.request.body).get('passenger_info_json', '') == '' or \
            json.loads(self.request.body).get('train_info_json', '') == '':
                self.finish({"status": '2', "desc": '参数异常', "result": 'train_date or from_station or to_station or passenger_info_json or train_info_json is: None'})
                return
            _ = yield tornado.gen.Task(task_buy, param_dict)

        elif api_name == '':
            self.finish('嘎哈呢')
            return
        else:
            self.finish({'status': '404', 'desc': '把自己好好劝一劝', 'result': '你走丢了'})
            return

        # 从redis集群中获取结果
        res = yield tornado.gen.Task(self.getResult, username)
        print res, type(res)
        print '='*30

        try: result = json.loads(res["result"].replace("'", '"')) # ! 神坑啊 !
        except: result = res

        result_dict = {
            "status": res["status"],
            "desc": res["desc"],
            "result": result
        }
        self.finish(result_dict)
        return


    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, api_name):
        # apk文件下载:正常人都是扔给nginx; 我不正常呗
        if api_name == 'apk':
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=huochepiao.apk')
            with open('./static/huochepiao.apk', 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data: break
                    self.write(data)
            self.finish()
            return
        else:
            self.finish({'status': '404', 'desc': '把自己好好劝一劝', 'result': '你走丢了'})
            return



class IndexHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous # 长连接, self.finish()才关闭连接
    @tornado.gen.coroutine # 仅仅是声明:这是个异步函数
    def get(self, *args, **kwargs):

        self.write('''
        <html>
          <head><title>Upload File</title></head>
          <body>
            <form action='/' enctype="multipart/form-data" method='post'>
            <input type='file' name='file'/><br/>
            <input type='text' name='pwd' value='输入秘钥'/><br/>
            <input type='submit' value='submit'/><br/>
            </form>
          </body>
        </html>
        ''')
        if self.get_argument('key', '') == 'HuoyanBot':
            with open('./static/userpwd.txt', 'r') as f:
                while True:
                    data = f.readline()
                    if not data: break
                    self.write('<div>'+data+'</div>')
        self.finish('这是首页啊?!建设中...')
        return

    @tornado.web.asynchronous # 长连接, self.finish()才关闭连接
    @tornado.gen.coroutine # 仅仅是声明:这是个异步函数
    def post(self, *args, **kwargs):
        if self.get_argument('pwd') == 'HuoyanBot':
            #文件的暂存路径
            # upload_path=os.path.join(os.path.dirname(__file__),'files')
            upload_path = './static/'
            #提取表单中‘name’为‘file’的文件元数据
            file_data = self.request.files['file'][0]['body']
            filename = 'huochepiao.apk'
            filepath = os.path.join(upload_path,filename)
            #有些文件需要已二进制的形式存储，实际中可以更改
            with open(filepath,'wb') as f:
                f.write(file_data)
            self.write('上传成功!')
        self.finish('好好劝劝自己, 别老瞎试')
        return