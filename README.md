### Apimock
Api接口 mock server返回，用于app api容错测试

#原理：

该mock指 mock，api服务器端返回的response

app通过代理wifi访问pc，pc开fiddler(或anyproxy)抓包，经二次开发fiddler(anyproxy)，将指定数据包劫持发给 mockserver ，mockserver会根据其内部定义的规则篡改数据包并返回给fiddler(anyproxy)，完成一次mock

启动mockserver后 

轮询mock---会根据黑白名单 依次对api 的各json字段做fuzz mock，之后当再次劫持该api时执行一种fuzz


fuzz规则：
A.json字段的fuzz
'fun:del','fun:more','fun:blank','fun:none','fun:null','fun:0','fun:-1','fun:0.00002','fun:2.00001','fun:maxint','fun:maxlong','fun:*n','fun:/n','fun:ext','fun:cut','fun:overlen','fun:illega'

B.body相关的fuzz
'body={}','body=abc{}','code=404','code=502','code=302','net=delay'

另外可通过proxy.py来注入篡改规则 ,完成注入后 app再次访问api来进行Mock测试


conf.yml配置文件： 
pairwisetest : False  是否使用正交算法
combination : False  是否使用用例组合算法
specialapi :          特殊api,将使用对应项和值作api区分
- "/index.php?method"  
#- "/index.php?method,__version,__channel"
whitelist:    白名单
-"/index.php?method=clientconf.firstscreen&__version=3.0.6.3203&__plat=android&__channel=guanwang"
#- "/index.php?method=clientconf.firstscreen"
#- "/index.php?"

blacklist: 黑名单
#-"index.php?method=clientconf.firstscreen&__version=3.0.6.3203&__plat=android&__channel=guanwang"
getobjfromnet : False  用例mock集合是否从web上获取及存储
batch: 4  用例模式每次执行多少条case （单独的mockserver未使用该项）

Obj.yml 配置文件：
抓取白名单中api 并将需要执行的mock测试case记录到该文件中，可自定义配置设置哪些需要执行（删除或#）

Tested.yml 配置文件：
将已经测试过的case记录到该文件，可断点续测后续case

运行时log:
current testing Api : /ajax_get_myinfo?option,roomid,_  （当前正在测试的api）

current testing mock Queue :   (当前mock规则队列，显示当前mock规则及+4)
num = 9
['errno=fun:del', 'errno=fun:more', 'errno=fun:blank', 'errmsg=fun:del', 'errmsg=fun:more']

current testing mock key : （当前mock规则）
errno=fun:del

current server state :  （当前mock server内部状态机）
ishang|type|api|key|value|time|body|code|delay
False
key
['/ajax_get_myinfo']
['errno']
{'errno': 'fun:del'}
0
{}
200


#运行：

1.将fiddlerjs/fiddler.js 内容复制替换到 fiddler->Rules->Customize Rules中

  （或anyproxy -i --rule anyproxyjs.js --intercept   启动anyproxy 定制使用anyproxyjs.js 启用https劫持)

  并修改filterUrl="panda.tv"  来劫持指定域名的数据包 （anyproxy 修改anyproxyjs.js中host）
  
2.启动mockserver.py（按规则轮询mock 或 动态注入mock）

3.动态运行 python proxy.py xxx 来注入规则

  -p 1    hang住server内部状态
  -p 0    解除hang

  -a xxx  劫持修改具体某个api  或不定义则修改任意api
  
  -r 1    清空已经定义的规则
  
  -s 5    server暂停5s再返回，模拟服务器hang
  
  -d 2g   模拟2g网络
  
  -d 100  延迟100毫秒，模拟网络延迟
  
  -c 404  返回404

  -b xx   篡改整个body，可以是非json
  
  -k data.uid=1 修改路径为data.uid的键值为1
     
  -k re:name=zhao 修改正则表达式为name的键值为zhao
  
            =fun:xxx  xxx是内部快捷函数
            
            内部函数如下：
            
            fun:del 删除该键
            
            fun:more 兄弟节点下添加多余的其他键
            
            fun:blank 键值为''  ,fun:none,fun:null,fun:0,fun:-1,fun:0.00002,fun:2.00001,fun:maxint,fun:maxlong
            
            fun:*n 数字n倍  ,fun:/n 除n
            
            fun:ext 字符串延长  ,fun:cut 缩短
            
            fun:overlen 超长
            
            fun:illega 非法字符
           
  （anyproxy 暂不支持-c -d -s）
  
例子：

　　Python proxy.py -p 1
　　Python proxy.py -p 0
  
    python proxy.py -a /api/user/get -k errno=1   
  
    python proxy.py -a /api/user/get -k re:name="H1 \u266a@\u5c0f\u8776\u6c42\u5b88\u62a4"

    python proxy.py -r 1
  
    python proxy.py -s 5

    python proxy.py -d 150

    python proxy.py -d 2g

    python proxy.py -b {}

    python proxy.py -a /api/user/get -k re:name=fun:del

    python proxy.py -a /api/user/get -k data.uid=fun:maxint