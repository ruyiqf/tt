# coding: utf-8
import os
import time

from .tdxdll import DLLError
from .tdxdll import TDXDLL
from . import helpers
from .log import log

# 表示查询信息的种类，0资金  1股份   2当日委托  3当日成交     4可撤单   5股东代码  6融资余额   7融券余额  8可融证券
QueryType = {
    "balance": 0,
    "positions": 1,
    "today_entrust": 2,
    "today_commit": 3,
    "cancancel": 4,
    "gddm": 5,
    "rzye": 6,
    "rqye": 7,
    "krzq": 8
}
OrderTYpe = {
#表示委托的种类，0买入 1卖出  2融资买入  3融券卖出   4买券还券   5卖券还款  6现券还券
# todo: 两融的名字不会翻译， 先拼音放着了。
    "buy": 0,
    "sell": 1,
    "rzbuy": 2,
    "rqsell": 3,
    "mqhq": 4,
    "mqhk": 5,
    "xqhq": 6
}

class NotLoginError(Exception):
    def __init__(self, result=None):
        super(NotLoginError, self).__init__()
        self.result = result


class TDXTrader:
    global_config_path = os.path.dirname(__file__) + '/config/global.json'
    config_path = os.path.dirname(__file__) + '/config/tdx.json'

    def __init__(self):
        self.account_config = None
        self.s = None
        self.exchange_stock_account = dict()

        self.__read_config()
        self.dll = TDXDLL()

        self.exchange_stock_account = dict()

    def login(self, throw=False):
        broker = self.account_config['broker']
        yyb = self.account_config['yybid']
        account = self.account_config['account']
        password = self.account_config['password']

        iplist = self.config[broker]

        for addr in iplist.values():
            log.info("attempt connect to {}".format(addr))
            ip, port = addr.split(':')
            try:
                self.dll.logon(ip, int(port), yyb, account, password)
                log.info("connect to {} successed!".format(addr))
                self.get_share_holder_account()
                return True
            except DLLError as e:
                log.info(e)
        if throw:
            raise NotLoginError("无法连接broker: {}".format(broker))

    def logoff(self):
        self.dll.logoff()

    def prepare(self, need_data):
        """登录的统一接口
        :param need_data 登录所需数据
        """
        self.read_config(need_data)
        self.autologin()

    def autologin(self, limit=3):
        """实现自动登录
        :param limit: 登录次数限制
        """
        for _ in range(limit):
            if self.login():
                break
            else:
                time.sleep(10 * _)  # 每次重试增加间隔
        else:
            print(
                u'{} 登录失败次数过多, 请检查密码是否正确 / 券商服务器是否处于维护中 / 网络连接是否正常'.format(time.strftime('%H:%M:%S', time.localtime())))
            raise NotLoginError('登录失败次数过多, 请检查密码是否正确 / 券商服务器是否处于维护中 / 网络连接是否正常')
        # self.keepalive()  # 接口本身似乎带心跳， 先观察



    def _query(self, querytype):
        success, data = self.dll.querydata(querytype)
        if success:
            return format_result(data)
        else:
            log.info("error: " + data)
            return ""

    @property
    def balance(self):
        return self.get_balance()

    def get_balance(self):
        """获取账户资金状况"""
        return self._query(QueryType["balance"])

    @property
    def position(self):
        return self.get_position()

    def get_position(self):
        """获取持仓"""
        return self._query(QueryType["positions"])

    @property
    def entrust(self):
        return self.get_entrust()

    def get_entrust(self):
        """获取当日委托列表"""
        return self._query(QueryType["today_entrust"])

    @property
    def commits(self):
        return self.get_entrust()

    def get_commits(self):
        """获取当日委托列表"""
        return self._query(QueryType["today_commit"])

    def get_can_cancel(self):
        """获取当日委托列表"""
        return self._query(QueryType["cancancel"])
    def get_share_holder_account(self):
        data = self._query(QueryType["gddm"])

        for d in data:
            self.exchange_stock_account[d['帐号类别']] = d['股东代码']

        return self.exchange_stock_account
    def check_available_cancels(self):
        pass

    def cancel_entrust(self, entrust_no, stock_code):
        pass

    def cancel_entrusts(self, entrust_no):
        pass

    @property
    def current_deal(self):
        return self.get_current_deal()

    def get_current_deal(self):
        pass

    def buy(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
        pass

    def sell(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
        pass

    def __trade(self, stock_code, price, entrust_prop, other):
        pass

    def __get_trade_need_info(self, stock_code):
        pass

    def format_response_data(self, data):
        pass

    def check_account_live(self, response):
        pass

    def heartbeat(self):
        pass

    def __read_config(self):
        """读取 config"""
        self.config = helpers.file2dict(self.config_path)
        self.global_config = helpers.file2dict(self.global_config_path)
        self.config.update(self.global_config)

    def read_config(self, path):
        try:
            self.account_config = helpers.file2dict(path)
        except ValueError:
            log.error('配置文件格式有误，请勿使用记事本编辑，推荐使用 notepad++ 或者 sublime text')
        for v in self.account_config:
            if type(v) is int:
                log.warn('配置文件的值最好使用双引号包裹，使用字符串类型，否则可能导致不可知的问题')


def format_result(data):

    lines = data.split("\n")
    head = True
    body = []
    for line in lines:
        if head:
            heads = line.split("\t")
        else:
            fields = line.split("\t")
            body.append(dict(zip(heads, fields)))
        head = False
    #print (heads)
    #print(body)
    return body


