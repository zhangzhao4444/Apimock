#!/usr/bin/evn python
# -*- coding:utf-8 -*-
# @author: zhangzhao_lenovo@126.com
# @date: 20161027
# @version: 1.0.0.1026

import selectors
import socket
import time
import json
import re
import random
from decimal import Decimal

class server:
    def __init__(self):
        self._sock = socket.socket()
        self._selector = selectors.DefaultSelector()
        self.init()

    def init(self):
        self.time = 0
        self.type = ''
        self.delay = ''
        self.code = 200
        self.body ='{}'
        self.json=1
        self.api=[]
        self.key = []
        #self.value={'re:NAMES':'xx','re:name':'H1 \u266a@\u5c0f\u8776\u6c42\u5b88\u62a4','errno':'1','data.uid':'fun:del','regex:^is_.*':'999'}
        self.value = {}

    def mock(self, type, data):
        def funclist(type,json,k,v,kv):
            def delkey(json,k):
                del json[k]

            def more(json,k,v):
                tmp={}
                tmp['test1']='H1 \u266a@\u5c0f\u8776\u6c42\u5b88\u62a4'
                tmp['test2']=0
                json.update(tmp)

            def set(json,k,v):
                json[k]=v

            def setintmultin(json, k,v):
                if isinstance(v, int):
                    n = random.randint(2, 199)
                    json[k]=str(Decimal(v) * Decimal(n))

            def setintdivn(json, k,v):
                if isinstance(v, int):
                    n = random.random()
                    json[k]=str(Decimal(v) * Decimal(n))

            def setstrextend(json, k,v):
                v1=''
                for i in range(0,random.randint(2, 19)): v1 += str(v)
                json[k] = v1

            def setstrshorten(json, k,v):
                v=str(v)
                v1=''
                n = random.randint(1, len(v)-1)
                v1 = (len(v) <= 3) and v or v[0:len(v) - n]
                json[k] = v1

            def setstroverlen(json, k,v):
                v=str(v)
                n = 1025
                # n=4294967294  max string ,..dot use!
                for i in range(0, n): v += '1'
                json[k] = v

            def setstrillega(json, k,v):
                json[k] = str(v) + ',*&#%()='[random.randint(1, 8) - 1] + 'H1 \u266a@\u5c0f\u8776\u6c42\u5b88\u62a4'

            list = {   'del': lambda: delkey(json,k),
                       'more': lambda: more(json,k,v),
                       'blank': lambda: set(json,k,' '),
                       'none': lambda: set(json,k,None),
                       'null': lambda: set(json,k,''),
                       '0': lambda: set(json,k,0),
                       '-1': lambda: set(json,k,-1),
                       '0.00002': lambda: set(json, k,0.00002),
                       '2.00001': lambda: set(json, k,2.00001),
                       'maxint': lambda: set(json, k, 2147483648),
                       'maxlong': lambda: set(json, k, 9223372036854775808),
                       '*n': lambda: setintmultin(json, k,kv),
                       '/n': lambda: setintdivn(json, k, kv),
                       'ext': lambda: setstrextend(json, k, kv),
                       'cut': lambda: setstrshorten(json, k, kv),
                       'overlen': lambda: setstroverlen(json, k, kv),
                       'illega': lambda: setstrillega(json, k, kv),
                       }
            return list[type]()

        def dofun(json,k,v,kv):
            if ':' in v:
                flag, func = v.split(':', 1)
                if flag in ['fun', 'func', 'funcation']:
                    funclist(func,json,k,v,kv)
            else:
                json[k] = v
            return json

        def regexpsearch(json,regexp,value):
            ret = json
            data = ret
            if isinstance(json, dict):
                for k in list(json):
                    v=json[k]
                    if re.search(regexp, k):
                        dofun(ret, k, value, ret[k])
                    regexpsearch(v, regexp, value)
            return data

        def exactsearch(json, l_key ,value):
            ret = json
            data = ret
            for k in l_key:
                if isinstance(k, str):
                    if k not in ret: return json
                    if not (isinstance(ret[k], dict)):
                        dofun(ret, k, value,ret[k])
                        return data
                else:return json
                ret = ret[k]
            return data

        def sleep(data):
            time.sleep(self.time)
            return data

        def delay(data):
            data['mock']['delay'] = str(self.delay)
            return data

        def code(data):
            data['mock']['responsecode'] = str(self.code)
            return data

        def body(data):
            try: body = json.loads(data)
            except :
                self.json=0
                return data
            body['mock'] = {}
            return body

        def key(data):
            for k in self.key:
                v= self.value[k]
                if ':' in k:
                    str,k = k.split(':',1)
                    if str.lower() in ['regex','re','regexp']: data = regexpsearch(data,k,v)
                else:
                    l_key= k.split('.')
                    data = exactsearch(data,l_key,v)
            return data


        mockfun = {'sleep': lambda: sleep(data),
                   'delay': lambda: delay(data),
                   'code': lambda :code(data),
                   'body': lambda: body(self.body),
                   'key': lambda: key(data),
                   'nobody':lambda: body('{}'),
                   '': lambda: data,
                   'clear':lambda : self.init()}
        return mockfun[self.type]()

    def start(self):
        sock = self._sock
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setblocking(0)
        sock.bind(('',8390))
        sock.listen(100)
        selector = self._selector
        self.add_handler(sock.fileno(), self._accept, selectors.EVENT_READ)
        while True:
            events = selector.select(1)
            for key, event in events:
                handler, data = key.data
                if data:
                    handler(**data)
                else :
                    handler()

    def _accept(self):
        for i in range(100):
            try:
                conn, address = self._sock.accept()
            except OSError:
                break
            else:
                conn.setblocking(0)
                fd = conn.fileno()
                self.add_handler(fd, self._read, selectors.EVENT_READ, {'conn': conn})

    def _read(self, conn):
        fd = conn.fileno()
        self.remove_handler(fd)
        try:
            data=conn.recv(16384).decode('utf8')
            api,body = data.split(':',1)
            #print(data)
            if api=='mockconfig':
                try:
                    self.config(body)
                except Exception as e:
                    print(e)
                conn.close()
                return
        except:
            conn.close()
            raise
        else:
            self.add_handler(fd, self._write, selectors.EVENT_WRITE, {'conn': conn, 'data':data})

    def _write(self, conn, data):
        fd = conn.fileno()
        self.remove_handler(fd)
        try:
            conn.sendall(self.prep(data).encode('utf8'))
        finally:
            conn.close()

    def prep(self,data):
        api, data = data.split(':', 1)
        data = json.loads(data, encoding="utf8")
        mock = {}
        data['mock'] = mock
        if api in self.api or not self.api:
            print(api)
            print(' msg body : ')
            print(data)
            try:
                data = self.mock('', data)
            except Exception as e:
                print(e)
        if self.json == 1:
            if 'responsecode' not in data['mock']: data['mock']['responsecode'] = '200'
            if 'delay' not in data['mock']: data['mock']['delay'] = 0
            data = json.dumps(data)
        print(' mock : ')
        print(data)
        self.json = 1
        return data

    def config(self,data):
        def config(type,data):
            def configapi(data):
                data not in self.api and self.api.append(data)

            def configsleep(data):
                self.type = type
                self.time = int(data)

            def configdelay(data):
                self.type = type
                self.delay = data

            def configcode(data):
                self.type = type
                self.code = int(data)

            def configbody(data):
                self.type = type
                self.body= str(data)

            def configkey(data):
                key,value=data.split('=',1)
                self.type = type
                if key not in self.key:
                    self.key.append(key)
                    self.value[key]=value
                else:
                    del self.value[key]
                    self.value[key] = value

            def clear(data):
                data and self.init()

            switch = { 'api': lambda: configapi(data),
                       'sleep': lambda: configsleep(data),
                       'delay': lambda: configdelay(data),
                       'code': lambda: configcode(data),
                       'body': lambda: configbody(data),
                       'key': lambda: configkey(data),
                       'clear': lambda: clear(data),}
            return switch[type]()

        cmd = json.loads(data)
        for k,v in cmd.items():
            config(k,v)
        print('type|api|key|value|time|body|code|delay')
        print(self.type)
        print(self.api)
        print(self.key)
        print(self.value)
        print(self.time)
        print(self.body)
        print(self.code)
        print(self.delay)

    def add_handler(self, fd, handler, event, data=None):
        self._selector.register(fd, event, (handler, data))

    def remove_handler(self, fd):
        self._selector.unregister(fd)

if __name__ == "__main__":
    server().start()