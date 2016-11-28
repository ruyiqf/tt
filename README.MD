
### 1.部署
.py文件放到easytrader/easytrader目录下

tdx.json 放到easytrader/easytrader/config目录下， 里面的配置到网页查。

多ip会轮流尝试，第一个成功的返回。

[brokder].json 放到自己私有地方， prepare的时候指定目录即可。

[brokder].json里: 
  * broker指向tdx.json中的券商简称，建议按照tdx+简称命名， 如tdxxd表示信达证券 
  * yybid是营业部编码，到网页查 
  * version建议按网页填写， 填别的有没有问题不知道。

相关的dll都放入同一个目录tdxdlls

运行前， 把tdxdlls目录加入系统path中，或者把tdxdlls目录下所有dll拷贝到执行时的工作目录。

### 2. 配合修改
##### easytrader/api.py文件增加以下内容：
`from .tdxdll import TDXDLL
from .tdxtrader import TDXTrader
`
##### use函数增加：
`    elif broker.lower() in ['tdxxd']:
        return TDXTrader('tdxxd')
    ......
`
#### easytrader.__init__.py文件增加
`from .tdxdll import TDXDLL
from .tdxtrader import TDXTrader
`
### 3. 关于dll文件
**因为担心涉及到安全隐患，本处不提供, 也不要向我索取。需要的到网上自行搜索。 使用dll及本软件的风险自行承担**


20161127: 
  因为各个券商需要各自的dll文件， 所以要把traderXXX.dll改名为[brokder].dll, 以防止互相干扰

api中增加broker名作为初始化参数


