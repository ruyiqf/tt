# coding: utf-8
import os
import time
import re
from .tdxdll import DLLError, TDXDLL, QueryType, OrderType, PriceType
from . import helpers
from .log import log


class NotLoginError(Exception):
    def __init__(self, result=None):
        super(NotLoginError, self).__init__()
        self.result = result

thedll =None # 将thedll放到全局变量，防止因为作为对象的属性，导致pickle失败
class TDXTrader:
    global_config_path = os.path.dirname(__file__) + '/config/global.json'
    config_path = os.path.dirname(__file__) + '/config/tdx.json'

    def __init__(self, broker):
        global thedll
        self.account_config = None
        self.s = None
        self.exchange_stock_account = dict()

        self.__read_config()
        thedll = TDXDLL(broker)

        self.exchange_stock_account = dict()

    # #####################################################################
    # 初始化、登录类方法
    # #####################################################################

    def prepare(self, need_data):
        """登录的统一接口
        :param need_data 登录所需数据
        """
        self.read_config(need_data)
        self.autologin()

    def login(self, throw=False):
        broker = self.account_config['broker']
        yyb = self.account_config['yybid']
        account = self.account_config['account']
        password = self.account_config['password']
        version = self.account_config['version'] 
        iplist = self.config[broker]

        for addr in iplist.values():
            log.info("attempt connect to {}".format(addr))
            ip, port = addr.split(':')
            try:
                thedll.logon(ip, int(port), version, yyb, account, password)
                log.info("connect to {} successed!".format(addr))
                self.get_share_holder_account()
                return True
            except Exception as e:
            	  log.info(e)
            	  time.sleep(1)
        if throw:
            raise NotLoginError("无法连接broker: {}".format(broker))

    def logoff(self):
        thedll.logoff()

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

    # #####################################################################
    # 查询类方法
    # #####################################################################

    def _query(self, querytype):
        success, data = thedll.querydata(querytype)
        if success:
            return self.format_response_data(data)
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

    def get_can_cancel(self):
        """获取当日委托列表"""
        return self._query(QueryType["cancancel"])

    def get_share_holder_account(self):
        data = self._query(QueryType["gddm"])

        for d in data:
            self.exchange_stock_account[d['帐号类别']] = d['股东代码']

        return self.exchange_stock_account

    def check_available_cancels(self):
        return self.get_can_cancel()

    @property
    def current_deal(self):
        return self.get_current_deal()

    def get_current_deal(self):
        return self._query(QueryType["today_deal"])

    # #####################################################################
    # 操作类方法
    # #####################################################################

    def _do(self, ordertype, pricetype, stock_code, price, quantity):
        sh_exchange_type = '1'
        sz_exchange_type = '0'
        exchange_type = sh_exchange_type if helpers.get_stock_type(stock_code) == 'sh' else sz_exchange_type
        gddm = self.exchange_stock_account[exchange_type]

        success, data = thedll.sendorder(ordertype, pricetype, gddm, stock_code, price, quantity)

        if success:
            return self.format_response_data(data)
        else:
            log.info("error: " + data)
            return ""

    def buy(self, stock_code, price, amount=0., volume=0, entrust_prop=0):
        vol = volume if volume > 0 else (amount/price // 100) * 100
        pricetype = PriceType(entrust_prop) if type(entrust_prop) == "str" else entrust_prop
        return self._do(OrderType["buy"], pricetype, stock_code, price, vol)

    def sell(self, stock_code, price, amount=0, volume=0, entrust_prop=0):
        vol = volume if volume > 0 else (amount/price // 100) * 100
        pricetype = PriceType(entrust_prop) if type(entrust_prop) == "str" else entrust_prop
        return self._do(OrderType["sell"], pricetype, stock_code, price, vol)

    def cancel_entrusts(self, entrust_no):
        entrusts = self.get_can_cancel()
        for e in entrusts:
            if e['委托编号'] == entrust_no:
                exchangeid = e['交易所代码']
                success, data = thedll.cancelorder(exchangeid, entrust_no)
                return success
        return False

    def cancel_entrust(self, entrust_no, stock_code):
        pass

    # #####################################################################
    # 其它查询类方法
    # #####################################################################

    # todo: 历史查询 0历史委托  1历史成交   2交割单 (做的必要行不大？)

    # todo: 查询某股票的实时5档行情(似乎有用， 感觉券商行情比用网络免费行情源要可靠， 可以替代easyquotation)

    def get_last_errmsg(self):
        return thedll.get_last_errmsg()

    def get_last_result(self):
        return thedll.get_last_result()
    # #####################################################################
    # 辅助类方法
    # #####################################################################

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

    def format_response_data_type(self, response_data):
        """格式化返回的值为正确的类型
        :param response_data: 返回的数据
        """
        if type(response_data) is not list:
            return response_data

        int_match_str = '|'.join(self.config['response_format']['int'])
        float_match_str = '|'.join(self.config['response_format']['float'])
        for item in response_data:
            for key in item:
                try:
                    if re.search(int_match_str, key) is not None:
                        item[key] = helpers.str2num(item[key], 'int')
                    elif re.search(float_match_str, key) is not None:
                        item[key] = helpers.str2num(item[key], 'float')
                except ValueError:
                    continue
        return response_data

    def format_response_data(self, data):

        lines = data.split("\n")
        field_heads = []
        body = []
        firstline = True
        for line in lines:
            if firstline:
                field_heads = line.split("\t")
                firstline = False
            else:
                fields = line.split("\t")
                body.append(dict(zip(field_heads, fields)))
        return self.format_response_data_type(body)

# #####################################################################
# 辅助类函数
# #####################################################################



