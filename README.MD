
1. .py文件放到easytrader/easytrader目录下
tdx.json 放到easytrader/easytrader/config目录下， 里面的配置到下面说的网页查
多ip会轮流尝试，第一个成功的返回。

xd.json 放到自己私有地方， prepare的时候指定目录即可。
xd.json里，broker指向tdx.json中的券商简称， yybid是营业部编码，到网页查 http://www.chaoguwaigua.com/downloads/qszl.htm 



2.相关的dll都放入同一个目录tdxdlls
运行前， 把tdxdlls目录加入系统path中，或者把tdxdlls目录下所有dll拷贝到执行时的工作目录。

-- @老杜

