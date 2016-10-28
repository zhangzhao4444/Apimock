### Apimock
Api接口 mock server返回，用于app api容错测试

#原理：

该mock指 mock，api服务器端返回的response

app通过代理wifi访问pc，pc开fiddler抓包，经二次开发fiddler，将指定数据包劫持发给 mockserver ，mockserver会根据其内部定义的规则篡改数据包并返回给fiddler，完成一次mock

启动mockserver后 通过proxy.py来注入篡改规则 ,完成注入后 app再次访问api来进行Mock测试

#运行：

1.将fiddlerjs/fiddler.js 内容复制替换到 fiddler->Rules->Customize Rules中

  并修改filterUrl="www.3663.com"  来劫持指定域名的数据包
  
2.启动mockserver.py

3.动态运行 python proxy.py xxx 来定义规则

  -a xxx  劫持修改具体某个api  或不定义则修改任意api
  
  -r 1    清空已经定义的规则
  
  -s 5    server暂停5s再返回，模拟服务器hang
  
  -d 2g   模拟2g网络
  
  -d 100  延迟100毫秒，模拟网络延迟

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
           
            
  
例子：
  
    python proxy.py -a /api/user/get -k errno=1   
  
    python proxy.py -a /api/user/get -k re:name="H1 \u266a@\u5c0f\u8776\u6c42\u5b88\u62a4"

    python proxy.py -r 1
  
    python proxy.py -s 5

    python proxy.py -d 150

    python proxy.py -d 2g

    python proxy.py -b {}

    python proxy.py -a /api/user/get -k re:name=fun:del

    python proxy.py -a /api/user/get -k data.uid=fun:maxint
