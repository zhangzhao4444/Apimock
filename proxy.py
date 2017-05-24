#!/usr/bin/evn python
# -*- coding:utf-8 -*-
# @author: zhangzhao_lenovo@126.com
# @date: 20161027
# @version: 1.0.0.1003

from socket import *
from optparse import OptionParser
import json

def loading():
    while True:
        for i in ["/", "-", "|", "\\", "|"]:
            print("%s" % i, end='\r')

def connect(port=8390):
    address = ('127.0.0.1',port)
    s = socket(AF_INET,SOCK_STREAM)
    s.connect(address)
    return s

def send(s,str):
    s.sendall(str.encode('utf8'))

def cmd():
    usage = "python proxy.py -k key=value"
    cmd = OptionParser(usage)
    cmd.add_option("-s", "--sleep", type="int", dest="sleep",help=" python proxy -s 5 ,sleep 5秒后返回json" )
    cmd.add_option("-d", "--delay", type="string", dest="delay",help=" python proxy -d 150 ,延迟150毫秒后返回json" )
    cmd.add_option("-b", "--body", type="string", dest="body",help=" python proxy -b {} ,返回的body={}")
    cmd.add_option("-c", "--code", type="int", dest="code",help=" python proxy -c 404 ,返回的response code=404")
    cmd.add_option("-r", "--clear", type="int", dest="clear", default=0,help=" python proxy -r 1 ,清空内部state")
    cmd.add_option("-k", "--key", type="string", dest="key",help=" python proxy -k errno=1 ,返回json中errno字段=1" )
    cmd.add_option("-a", "--api", type="string", dest="api",help=" python proxy -a /api/user/get ,将/api/user/get接口加入待劫持api队列中"  )
    cmd.add_option("-p", "--pause",type = "int",dest="pause",help=" python proxy -p 1/0 ,1暂停轮询机制 ,0启用轮询" )
    (options, args) = cmd.parse_args()
    cmd={}
    list=['sleep','delay','body','code','clear','key','api','pause']
    for k in list:
        v = eval('options.'+k)
        if k=='pause' and (v==0 or v==1) :cmd[k] = v
        elif v: cmd[k] = v
    return cmd

if __name__ == "__main__":
    cmd = cmd()
    str=json.dumps(cmd)
    str='mockconfig:' + str
    print(str)
    try:
        conn = connect()
        conn.sendall(str.encode('utf8'))
    finally:
        conn.close()

#python proxy.py -a /api/user/get -k errno=1
#python proxy.py -a /api/user/get -k re:name="H1 \u266a@\u5c0f\u8776\u6c42\u5b88\u62a4"
#python proxy.py -r 1
#python proxy.py -s 5
#python proxy.py -d 150
#python proxy.py -d 2g
#python proxy.py -b {}
#python proxy.py -a /api/user/get -k re:name=fun:del
#python proxy.py -a /api/user/get -k data.uid=fun:maxint

