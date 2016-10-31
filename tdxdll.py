from ctypes import *
import ctypes.util as ctypesutil


class DLLError(Exception):
    def __init__(self, result=None):
        super(DLLError, self).__init__()
        self.result = result

# //开发文档
# //
#
# //1.交易API均是Trade.dll文件的导出函数，包括以下函数：
# //基本版的9个函数：
# // void  OpenTdx();//打开通达信
# // void  CloseTdx();//关闭通达信
# //  int  Logon(char* IP, short Port, char* Version, short YybID, char* AccountNo,char* TradeAccount, char* JyPassword,
# //             char* TxPassword, char* ErrInfo);//登录帐号
# // void  Logoff(int ClientID);//注销
# // void  QueryData(int ClientID, int Category, char* Result, char* ErrInfo);//查询各类交易数据
# // void  SendOrder(int ClientID, int Category ,int PriceType,  char* Gddm,  char* Zqdm , float Price, int Quantity,
# //                 char* Result, char* ErrInfo);//下单
# // void  CancelOrder(int ClientID, char* ExchangeID, char* hth, char* Result, char* ErrInfo);//撤单
# // void  GetQuote(int ClientID, char* Zqdm, char* Result, char* ErrInfo);//获取五档报价
# // void  Repay(int ClientID, char* Amount, char* Result, char* ErrInfo);//融资融券账户直接还款

# ///交易接口执行后，如果失败，则字符串ErrInfo保存了出错信息中文说明；
# ///如果成功，则字符串Result保存了结果数据,形式为表格数据，行数据之间通过\n字符分割，列数据之间通过\t分隔。
# ///Result是\n，\t分隔的中文字符串，比如查询股东代码时返回的结果字符串就是
#
# ///"股东代码\t股东名称\t帐号类别\t保留信息\n
# ///0000064567\t\t0\t\nA000064567\t\t1\t\n
# ///2000064567\t\t2\t\nB000064567\t\t3\t"
#
# ///查得此数据之后，通过分割字符串， 可以恢复为几行几列的表格形式的数据
#
#
#
# //2.API使用流程为: 应用程序先调用OpenTdx打开通达信实例，一个实例下可以同时登录多个交易账户，每个交易账户称之为ClientID.
# //通过调用Logon获得ClientID，然后可以调用其他API函数向各个ClientID进行查询或下单; 应用程序退出时应调用Logoff注销ClientID,
# //最后调用CloseTdx关闭通达信实例.
# //OpenTdx和CloseTdx在整个应用程序中只能被调用一次.API带有断线自动重连功能，应用程序只需根据API函数返回的出错信息进行适当错误处理即可。

# 表示查询信息的种类，0资金  1股份   2当日委托  3当日成交     4可撤单   5股东代码  6融资余额   7融券余额  8可融证券
QueryType = {
    "balance": 0,
    "positions": 1,
    "today_entrust": 2,
    "today_deal": 3,
    "cancancel": 4,
    "gddm": 5,
    "rzye": 6,
    "rqye": 7,
    "krzq": 8
}
# 表示委托的种类，0买入 1卖出  2融资买入  3融券卖出   4买券还券   5卖券还款  6现券还券
# todo: 两融的名字不会翻译， 先拼音放着了。
OrderType = {
    "buy": 0,
    "sell": 1,
    "rzbuy": 2,
    "rqsell": 3,
    "mqhq": 4,
    "mqhk": 5,
    "xqhq": 6
}
# 报价方式 0上海限价委托 深圳限价委托 1(市价委托)深圳对方最优价格  2(市价委托)深圳本方最优价格  3(市价委托)深圳即时成交剩余撤销
# 4(市价委托)上海五档即成剩撤 深圳五档即成剩撤 5(市价委托)深圳全额成交或撤销 6(市价委托)上海五档即成转限价

PriceType = {
    "limit": 0,
    "szmarket_opponent_best": 1,
    "szmarket_self_best": 2,
    "szmarket_commit_to_cancel": 3,
    "market_level5_commit_to_cancel": 4,
    "szmarket_all_commit_or_cancel": 5,
    "shmarket_level5_commit_to_limit": 6
}


class TDXDLL:
    def __init__(self):
        self.sessionid = -1
        # dllpath = os.path.join(os.path.dirname(__file__), 'trader.dll')
        print(ctypesutil.find_library('trader.dll'))
        self.dll = windll.LoadLibrary('trader.dll')
        self.opentdx()

        self.errmsg = create_string_buffer(256)
        self.result = create_string_buffer(1024 * 1024)

    def get_last_errmsg(self):
        return self.errmsg.value.decode('gbk')

    def get_last_result(self):
        return self.result.value.decode('gbk')

    def opentdx(self):
        # /// <summary>
        # /// 打开通达信实例
        # /// </summary>
        # ///void   OpenTdx();
        self.dll.OpenTdx()

    def closetdx(self):
        # /// <summary>
        # /// 关闭通达信实例
        # /// </summary>
        # ///void   CloseTdx();
        self.dll.OpenTdx()

    def logon(self, ip, port, yyb, account, pwd):
        # /// <summary>
        # /// 交易账户登录
        # /// </summary>
        # /// <param name="IP">券商交易服务器IP</param>
        # /// <param name="Port">券商交易服务器端口</param>
        # /// <param name="Version">设置通达信客户端的版本号</param>
        # /// <param name="YybID">营业部代码，请到网址 http://www.chaoguwaigua.com/downloads/qszl.htm 查询</param>
        # /// <param name="AccountNo">完整的登录账号，券商一般使用资金帐户或客户号</param>
        # /// <param name="TradeAccount">交易账号，一般与登录帐号相同. 请登录券商通达信软件，查询股东列表，
        # ///                            股东列表内的资金帐号就是交易帐号, 具体查询方法请见网站“热点问答”栏目</param>
        # /// <param name="JyPassword">交易密码</param>
        # /// <param name="TxPassword">通讯密码</param>
        # /// <param name="ErrInfo">此API执行返回后，如果出错，保存了错误信息说明。一般要分配256字节的空间。没出错时为空字符串。</param>
        # /// <returns>客户端ID，失败时返回-1</returns>
        # ///  int  Logon(char* IP, short Port, char* Version,short YybID,  char* AccountNo,char* TradeAccount,
        # ///             char* JyPassword,   char* TxPassword, char* ErrInfo);
        sessionid = self.dll.Logon(ip.encode(),
                                   port,
                                   b'6.50',
                                   yyb,
                                   account.encode(),
                                   account.encode(),
                                   pwd.encode(),
                                   b'',
                                   self.errmsg
                                   )  # 登录帐号
        if sessionid == -1:
            raise DLLError(self.errmsg.value)
        self.sessionid = sessionid
        return True

    def logoff(self):
        # /// <summary>
        # /// 交易账户注销
        # /// </summary>
        # /// <param name="ClientID">客户端ID</param>
        # /// void  Logoff(int ClientID);
        self.dll.Logoff(self.sessionid)

    def querydata(self, category):
        # /// <summary>
        # /// 查询各种交易数据
        # /// </summary>
        # /// <param name="ClientID">客户端ID</param>
        # /// <param name="Category">表示查询信息的种类，0资金  1股份   2当日委托  3当日成交 4可撤单
        # ///                        5股东代码  6融资余额   7融券余额  8可融证券</param>
        # /// <param name="Result">此API执行返回后，Result内保存了返回的查询数据, 形式为表格数据，
        # ///                      行数据之间通过\n字符分割，列数据之间通过\t分隔。
        # ///                      一般要分配1024*1024字节的空间。出错时为空字符串。</param>
        # /// <param name="ErrInfo">同Logon函数的ErrInfo说明</param>

        self.dll.QueryData(self.sessionid, category, self.result, self.errmsg)
        return (True, self.get_last_result()) if self.errmsg.value == b"" else (False, self.get_last_errmsg())

    def sendorder(self, category, pricetype, gddm, zqdm, price, quantity):
        # /// <summary>
        # /// 下委托交易证券
        # /// </summary>
        # /// <param name="ClientID">客户端ID</param>
        # /// <param name="Category">表示委托的种类，0买入 1卖出  2融资买入  3融券卖出   4买券还券   5卖券还款  6现券还券</param>
        # /// <param name="PriceType">表示报价方式 0上海限价委托 深圳限价委托 1(市价委托)深圳对方最优价格
        # ///                         2(市价委托)深圳本方最优价格  3(市价委托)深圳即时成交剩余撤销
        # ///                         4(市价委托)上海五档即成剩撤 深圳五档即成剩撤 5(市价委托)深圳全额成交或撤销
        # ///                         6(市价委托)上海五档即成转限价
        # /// <param name="Gddm">股东代码, 交易上海股票填上海的股东代码；交易深圳的股票填入深圳的股东代码</param>
        # /// <param name="Zqdm">证券代码</param>
        # /// <param name="Price">委托价格</param>
        # /// <param name="Quantity">委托数量</param>
        # /// <param name="Result">同上,其中含有委托编号数据</param>
        # /// <param name="ErrInfo">同上</param>
        # /// void  SendOrder(int ClientID, int Category ,int PriceType,  char* Gddm,  char* Zqdm , float Price,
        # ///                 int Quantity,  char* Result, char* ErrInfo);

        self.dll.SendOrder(self.sessionid, category, pricetype, gddm.encode(), zqdm.encode(),
                           c_float(price), quantity, self.result, self.errmsg)
        return (True, self.get_last_result()) if self.errmsg.value == b"" else (False, self.get_last_errmsg())

    def cancelorder(self, exchangeid, wth):
        # /// <summary>
        # /// 撤委托
        # /// </summary>
        # /// <param name="ClientID">客户端ID</param>
        # /// <param name="ExchangeID">交易所ID， 上海1，深圳0(招商证券普通账户深圳是2)</param>
        # /// <param name="hth">表示要撤的目标委托的编号</param>
        # /// <param name="Result">同上</param>
        # /// <param name="ErrInfo">同上</param>
        # /// void  CancelOrder(int ClientID, char* ExchangeID, char* hth, char* Result, char* ErrInfo);
        self.dll.CancelOrder(self.sessionid, exchangeid.encode(), wth.encode(),self.result, self.errmsg)

        return (True, self.get_last_result()) if self.errmsg.value == b"" else (False, self.get_last_errmsg())
