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
    cmd.add_option("-s", "--sleep", type="int", dest="sleep")
    cmd.add_option("-d", "--delay", type="string", dest="delay")
    cmd.add_option("-b", "--body", type="string", dest="body")
    cmd.add_option("-c", "--code", type="int", dest="code")
    cmd.add_option("-r", "--clear", type="int", dest="clear", default=0)
    cmd.add_option("-k", "--key", type="string", dest="key", )
    cmd.add_option("-a", "--api", type="string", dest="api", )
    (options, args) = cmd.parse_args()
    cmd={}
    list=['sleep','delay','body','code','clear','key','api']
    for k in list:
        v=eval('options.'+k)
        if v: cmd[k]=v
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

