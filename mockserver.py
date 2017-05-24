#!/usr/bin/evn python
# -*- coding:utf-8 -*-
# @author: zhangzhao_lenovo@126.com
# @date: 20170426
# @version: 1.0.0.2001

import sys,os
sys.path.append('..')

import json
import random
import re
import selectors
import socket
import time
from collections import defaultdict
from collections import deque
from decimal import Decimal
try:
    from plugins import pairwise as pairwise
except Exception as e:
    import pairwise
import yaml
import requests
import signal

def tree():
    return defaultdict(tree)

def treetonode(d, y, s):
    '''
    :param d:  json tree
    :param y:  node
    :param s:  [node]
    :return:  s
    '''
    def c(x, y, k, p):
        if isinstance(y, dict):
            k.append(x)
            treetonode(y, k, p)
            k.remove(x)
        else:
            k.append(x)
            l = '.'.join(k)
            if l not in p: p.append(l)
            k.remove(x)
    if isinstance(d, list):
        treetonode(d[0],y,s)
        return
    for a, b in d.items():
        if isinstance(b, (list, tuple)):
            for x in b:c(a, x, y, s)
        else:c(a, b, y, s)
    y = []

def dictinsertdict(a,b):
    for k, v in a.items():
        x = b.get(k)
        if not x:b[k] = v
        else:
            if isinstance(v,dict):dictinsertdict(v, x)
            else:b[k] = v

def apiload(flag):
    apiobj = {}
    try:
        if flag:
            apiobj = requests.get('http://autotest.xingyan.admin.pandatv.com:8360/returnjson.json').json()
        else:
            path = '%s%sobj.yml' % (os.path.split(os.path.realpath(__file__))[0], os.path.sep)
            if os.path.exists(path):
                file = open(path, encoding='gbk')
                apiobj = json.load(file)
                file.close()
    except Exception as e: print(e)
    if not apiobj: apiobj = {}
    return apiobj

def apisave(obj,flag):
    try:
        if flag:
            requests.post("http://autotest.xingyan.admin.pandatv.com:8360/post", data=obj)
        else:
            path = '%s%sobj.yml' % (os.path.split(os.path.realpath(__file__))[0], os.path.sep)
            stream = open(path,'w')
            json.dump(obj,stream,sort_keys=True,indent=4)
            stream.close()
    except Exception as e:pass

def testedload():
    tested = {}
    try:
        path = '%s%stested.yml' % (os.path.split(os.path.realpath(__file__))[0], os.path.sep)
        if os.path.exists(path):
            file = open(path, encoding='gbk')
            tested = json.load(file)
            file.close()
    except Exception as e: print(e)
    if not tested: tested = {}
    return tested

def testedsave(obj):
    try:
        path = '%s%stested.yml' % (os.path.split(os.path.realpath(__file__))[0], os.path.sep)
        stream = open(path,'w')
        json.dump(obj,stream,sort_keys=True,indent=4)
        stream.close()
    except Exception as e:pass

def urlisinlist(url,list,keys):
    paramlist = [p for p in url.split('?')[-1].split(',')]
    for l in list:
        api,params = l.split('?')
        if api == url.split('?')[0]:
            flag = 1
            for p in params.split('&'):
                key,value = p.split('=')
                if key in keys: key = key + '=' + value
                if not key in paramlist:flag = 0
            if flag==1 or not params:return True
    return False

def urlstrip(url,special):
    api, param = url.split('?', 1)
    world = []
    for item in param.split('&'):
        key, value = item.split('=')
        for specialurl in special:
            specialapi,specialparam = specialurl.split('?', 1)
            if api == specialapi and key in specialparam.split(','):
                key = item
                break
        world.append(key)
    #[key.append(p.split('=')[0]) for p in param.split('&')]
    api_param = api + '?' + ','.join(world)
    return api,param,api_param

def apiisinlist(ap,list):
    for l in list:
        a, ps = ap.split('?')
        if '?' not in l and a == l: return True
        elif re.search(a,l):
                for p in ps.split(','):
                    if not re.search(p,l):return False
                return True
    return False
def reset(q,l):
    q.clear()
    [q.append(x) for x in l if x not in q]

def merge(a,b):
    return [i for i in a if i in b]

def nodestocases(nodes,keymocklist,type):
    keycases = []
    if type:
        keycases = ['='.join(x[::-1]) for _, x in enumerate(pairwise.all_pairs2([keymocklist, nodes]))]
    else:
        keycases = [x + '=' + y  for x in nodes for y in keymocklist]
    return keycases

def nodestopictcase(nodes,case,keymocklist):
    keycases = case
    eachcolumn = []
    for node in nodes:
        node = node.replace('.', 'zhangzhaoatpandatv')
        exec(node + "=['']")
        for key in keymocklist:
            exec(node + '.append(' + "'" + node + '=' + key + "'" + ')')
        eachcolumn.append(eval(node))
    neweachcolum = []
    for colum in eachcolumn:
        newcloum = []
        for node in colum:
            newcloum.append(node.replace('zhangzhaoatpandatv', '.'))
        neweachcolum.append(newcloum)
    for _, x in enumerate(pairwise.all_pairs2(neweachcolum)):
        keycases.append(x)
    return keycases

class testobj:
    def __init__(self):
        self.whichapi = ''
        self.whichparam = ''
        self.whichmock = ''
    def tostring(self):
        return '%s_%s_%s'%(self.whichapi,self.whichparam,self.whichmock)

# class jsontoobj(object):
#     def __init__(self, d):
#         for a, b in d.items():
#             if isinstance(b, (list, tuple)):setattr(self, a, [jsontoobj(x) if isinstance(x, dict) else x for x in b])
#             else:setattr(self, a, jsontoobj(b) if isinstance(b, dict) else b)

class server:
    def __init__(self,conf,apiobj):
        self._sock = socket.socket()
        self._selector = selectors.DefaultSelector()
        self.conf = conf
        self.apiobj = apiobj
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
        self.value = {}

        self.apicase = {}
        self.testedapi = deque()
        self.testingapilist = deque()
        self.testingapiresponsejsonkeyqueue = deque()
        self.testedapiresponsejsonkeyqueue = deque()
        self.testingkey = ''
        self.basemockstrategy = ['body={}','body=abc{}','code=404','code=502','code=302','net=delay']
        self.keymockstrategy = ['fun:del','fun:more','fun:blank','fun:none','fun:null','fun:0','fun:-1','fun:0.00002','fun:2.00001','fun:maxint','fun:maxlong','fun:*n','fun:/n','fun:ext','fun:cut','fun:overlen','fun:illega']
        self.testingbasemockqueue =deque(self.basemockstrategy)
        self.testingkeymockqueue = deque(self.keymockstrategy)
        self.pairwise = self.conf['pairwisetest']
        self.combination = self.conf['combination']
        self.blacklist = list(self.conf['blacklist'])
        self.whitelist = list(self.conf['whitelist'])
        if not self.whitelist:self.whitelist = []
        if not self.blacklist:self.blacklist = []
        self.currentWhichApiWhichParaWhichMocktestingobj = testobj()
        self.UiPath = '' #x_x_x_x
        self.lasttime = time.time()
        self.apihash = self.apiobjtohash()
        self.hangup = 0
        self.ready = 0
        self.testedobj = testedload()
        self.running = False
        self.finished = False
        self.apiiscometestisexecuted = 0

    def apiobjsave(self,api_param,jsonkeypath):
        if api_param not in self.apiobj:
            obj = {}
            for key in jsonkeypath:
                mock = []
                for m in self.keymockstrategy:
                    mock.append(m)
                obj[key] = mock
            mock = []
            for m in self.basemockstrategy:
                mock.append(m)
            obj['global'] = mock
            self.apiobj[api_param] = obj
            apisave(self.apiobj,self.conf['getobjfromnet'])

    def apiobjtohash(self):
        self.apihash = {}
        for api,obj in self.apiobj.items():
            L = []
            for key,value in obj.items():
                if not value:
                    if key == 'global': value = self.basemockstrategy
                    else: value = self.keymockstrategy
                for v in value:
                    if key == 'global':
                        L.append(v)
                    else:
                        L.append(key+'='+v)
            self.apihash[api] = L
        return self.apihash

    def start(self,**kw):
        self.running = True
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

    def add_handler(self, fd, handler, event, data=None):
        self._selector.register(fd, event, (handler, data))

    def remove_handler(self, fd):
        self._selector.unregister(fd)

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
            data = conn.recv(65535).decode('utf8')
            api, body = data.split(':', 1)
            if api == 'mockconfig':
                try:
                    self.hangup = 1
                    self.config(json.loads(body))
                    self.showconfig()
                except Exception as e: print(e)
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
            conn.sendall(self._prep(data).encode('utf8'))
        finally:
            conn.close()

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
                if isinstance(v, int): json[k]=str(Decimal(v) * Decimal(random.randint(2, 199)))

            def setintdivn(json, k,v):
                if isinstance(v, int): json[k]=str(Decimal(v) * Decimal(random.random()))

            def setstrextend(json, k,v):
                v1=''
                for i in range(0,random.randint(2, 19)): v1 += str(v)
                json[k] = v1

            def setstrshorten(json, k,v):
                v=str(v)
                if not len(v): json[k] = v
                json[k] = (len(v) <= 3) and v or v[0:len(v) - random.randint(1, len(v)-1)]

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
            if re.search('^fun:', v):
                _, func = v.split(':', 1)
                funclist(func,json,k,v,kv)
            else:
                json[k] = v
            return json

        def regexpsearch(json, str, v):
            ret = json
            data = ret
            if isinstance(json, dict):
                for k in list(json):
                    if re.search(str, k):
                        dofun(ret, k, v, ret[k])
                        continue
                    regexpsearch(ret[k], str, v)
            if isinstance(json, list): [regexpsearch(j, str, v) for j in json]
            return data

        def exactsearch(json, l_key ,v):
            def find(k, ret, v):
                if isinstance(ret, list):
                    for l in ret:
                        if find(k, l, v): return 1
                if k not in ret:
                    return 0
                if ret[k] and not (isinstance(ret[k], dict)) and not (isinstance(ret[k], list)) or k == l_key[-1]:
                    dofun(ret, k, v, ret[k])
                    return 0
                return 1
            ret = json
            data = ret
            for k in l_key:
                if not find(k, ret, v): break
                if isinstance(ret, list): ret = ret[0]
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
                self.time = 0
                self.type = ''
                self.delay = ''
                self.code = 200
                self.body = '{}'
                self.json = 1
                self.api = []
                self.key = []
                self.value = {}

            def setpause(data):
                self.hangup = data

            switch = { 'api': lambda: configapi(data),
                       'sleep': lambda: configsleep(data),
                       'delay': lambda: configdelay(data),
                       'code': lambda: configcode(data),
                       'body': lambda: configbody(data),
                       'key': lambda: configkey(data),
                       'clear': lambda: clear(data),
                       'pause': lambda: setpause(data),}
            return switch[type]()

        for k,v in data.items():
            config(k,v)

    def configkeymock(self,type,value):
        config = {}
        config[type] = value
        self.config(config)

    def configbasemock(self,type):
        def setbodynull():
            value = '{}'
            type = 'body'
            config = {}
            config[type] = value
            self.config(config)

        def setbodyillega():
            value = 'adb{}'
            type = 'body'
            config = {}
            config[type] = value
            self.config(config)

        def setcode404():
            value = 404
            type = 'code'
            config = {}
            config[type] = value
            self.config(config)

        def setcode502():
            value = 502
            type = 'code'
            config = {}
            config[type] = value
            self.config(config)

        def setcode302():
            value = 302
            type = 'code'
            config = {}
            config[type] = value
            self.config(config)

        def setnetdelay():
            value = '150'
            type = 'delay'
            config = {}
            config[type] = value
            self.config(config)

        def setnetsleep():
            value = 5
            type = 'sleep'
            config = {}
            config[type] = value
            self.config(config)

        list = {'body={}': lambda: setbodynull(),
                'body=abc{}': lambda: setbodyillega(),
                'code=404': lambda: setcode404(),
                'code=502': lambda: setcode502(),
                'code=302': lambda: setcode302(),
                'net=delay': lambda: setnetdelay(),
                'net=sleep': lambda: setnetsleep(),
                }
        return list[type]()

    def showconfig(self):
        print('\ncurrent server state :')
        print('ishang|type|api|key|value|time|body|code|delay')
        print(self.hangup)
        print(self.type)
        print(self.api)
        print(self.key)
        print(self.value)
        print(self.time)
        print(self.body)
        print(self.code)
        print(self.delay)

    def clearconfig(self):
        value = 1
        type = 'clear'
        config = {}
        config[type] = value
        self.config(config)

    def _prep(self,Ox0Data):
        url, Ox0Data = Ox0Data.split(':', 1)
        #print(Ox0Data)
        try:
            api, param, api_param = urlstrip(url,self.conf['specialapi'])
            Ox0Data = json.loads(Ox0Data, encoding="utf8")
        except Exception as e:
            #print(e)
            return Ox0Data

        if True:
            specialkeys = []
            for specialurl in self.conf['specialapi']:
                specialapi, specialparam = specialurl.split('?', 1)
                if api == specialapi : specialkeys = specialparam.split(',')
            if api_param not in self.testingapilist and not urlisinlist(api_param, self.blacklist, specialkeys) and (urlisinlist(
                    api_param, self.whitelist, specialkeys) or not self.whitelist)and api_param not in self.testedapi:
                nodes = []
                treetonode(Ox0Data, [], nodes)
                self.apiobjsave(api_param, nodes)
                self.testingapilist.append(api_param)
                hash = {}
                hash['tree'] = nodes
                keycases = nodestocases(nodes, self.keymockstrategy, self.pairwise)
                if self.combination:
                    keycases = nodestopictcase(nodes,keycases,self.keymockstrategy)
                if api_param in self.apihash: select = merge(self.apihash[api_param], keycases)
                else:select = keycases
                hash['keymock'] = select
                num = len(select)
                if api_param in self.apihash: select = merge(self.apihash[api_param], list(self.testingbasemockqueue))
                else:select = list(self.testingbasemockqueue)
                hash['basemock'] = select
                num += len(select)
                hash['testcasenum'] = num
                self.apicase[api_param] = hash
                Ox0Data = json.dumps(Ox0Data)
                return Ox0Data

            if not self.testingapilist:
                Ox0Data = json.dumps(Ox0Data)
                return Ox0Data

            if api_param == self.testingapilist[0] and not self.hangup:
                if time.time() - self.lasttime < 1:
                    Ox0Data = json.dumps(Ox0Data)
                    return Ox0Data
                self.clearconfig()
                print('---------------------------------------------------------')
                print('current testing Api : %s' % api_param)

                hash = self.apicase[api_param]
                if not self.ready:
                    keycases = hash['keymock']
                    basecase = hash['basemock']
                    if api_param in self.testedobj:
                        testedhash = self.testedobj[api_param]
                        for k,l in testedhash.items():
                            for v in l:
                                if k == 'global':
                                    basecase.remove(v)
                                else:
                                    self.testedapiresponsejsonkeyqueue.append( k + '='+ v)
                    for case in keycases:
                        if case not in self.testingapiresponsejsonkeyqueue and case not in self.testedapiresponsejsonkeyqueue: self.testingapiresponsejsonkeyqueue.append(case)
                    reset(self.testingbasemockqueue, basecase)
                    self.ready = 1

                if self.testingapiresponsejsonkeyqueue:
                    print('\ncurrent testing mock Queue : ')
                    print('num = %s' % len(self.testingapiresponsejsonkeyqueue))
                    a = print(list(self.testingapiresponsejsonkeyqueue)[0:5]) if len(self.testingapiresponsejsonkeyqueue) > 5 else print(list(self.testingapiresponsejsonkeyqueue))
                    self.testingkey = self.testingapiresponsejsonkeyqueue.popleft()
                    self.lasttime = time.time()
                    print('\ncurrent testing mock key : \n%s' % self.testingkey)
                    self.currentWhichApiWhichParaWhichMocktestingobj.whichapi = api
                    self.api.append(api_param)
                    if isinstance(self.testingkey, list):
                        self.currentWhichApiWhichParaWhichMocktestingobj.whichparam = 'combination'
                        self.currentWhichApiWhichParaWhichMocktestingobj.whichmock = '%s' % self.testingkey
                        for value in list(self.testingkey):
                            if value:
                                self.configkeymock('key', value)
                    else:
                        value = self.testingkey
                        self.currentWhichApiWhichParaWhichMocktestingobj.whichparam = self.testingkey.split('=')[0]
                        self.currentWhichApiWhichParaWhichMocktestingobj.whichmock = self.testingkey.split('=')[-1]
                        self.configkeymock('key', value)
                    self.showconfig()
                    if self.testingkey not in self.testedapiresponsejsonkeyqueue:
                        self.testedapiresponsejsonkeyqueue.append(self.testingkey)
                        k, v = self.testingkey.split('=')
                        if api_param in self.testedobj:
                            if k in self.testedobj[api_param]:
                                self.testedobj[api_param][k].append(v)
                            else:
                                case = []
                                case.append(v)
                                self.testedobj[api_param][k] = case
                        else:
                            tested = {}
                            case = []
                            case.append(v)
                            tested[k] = case
                            self.testedobj[api_param] = tested
                else:
                    if self.testingbasemockqueue:
                        if api_param not in self.api:self.api.append(api_param)
                        print('\ncurrent testing body basemock Queue : ')
                        print(list(self.testingbasemockqueue))
                        base = self.testingbasemockqueue.popleft()
                        print('\ncurrent testing mock key : \n%s' % base)
                        self.currentWhichApiWhichParaWhichMocktestingobj.whichapi = api
                        self.currentWhichApiWhichParaWhichMocktestingobj.whichparam = ''
                        self.currentWhichApiWhichParaWhichMocktestingobj.whichmock = base
                        self.configbasemock(base)
                        self.showconfig()
                        if api_param in self.testedobj:
                            if 'global' in self.testedobj[api_param]:
                                self.testedobj[api_param]['global'].append(base)
                            else:
                                case = []
                                case.append(base)
                                self.testedobj[api_param]['global'] = case
                        else:
                            tested = {}
                            case = []
                            case.append(base)
                            tested['global'] = case
                            self.testedobj[api_param] = tested
                        #print(self.testedobj)
                    else:
                        if self.testingapilist: self.testingapilist.popleft()
                        self.testedapi.append(api_param)
                        self.ready = 0
        ox0data = Ox0Data
        if isinstance(Ox0Data,list):
            ogbody = Ox0Data
            Ox0Data = {}
            Ox0Data['body'] = ogbody
            key = self.key
            for k in key:
                self.key.remove(k)
                self.key.append('body.'+k)
                value = self.value[k]
                del self.value[k]
                self.value['body.'+k]=value
        mock = {}
        Ox0Data['mock'] = mock
        if apiisinlist(api_param,self.api) or not self.api:
            try:
                Ox0Data = self.mock('', Ox0Data)
                self.apiiscometestisexecuted = 1
            except Exception as e:
                print(e)
        if self.json == 1:
            if 'responsecode' not in Ox0Data['mock']: Ox0Data['mock']['responsecode'] = '200'
            if 'delay' not in Ox0Data['mock']: Ox0Data['mock']['delay'] = 0
            Ox0Data = json.dumps(Ox0Data)
        self.json = 1
        if isinstance(ox0data, list):
            key = self.key
            for k in key:
                value = self.value[k]
                kt = k.replace('body.','')
                self.key.remove(k)
                self.key.append(kt)
                del self.value[k]
                self.value[kt] = value
        #print(Ox0Data)
        return Ox0Data

    def testedsave(self):
        testedsave(self.testedobj)

    def stop(self, signum, frame):
        if self.running == True:
            self.running = False
            print('test finished! save testedobj')
            testedsave(self.testedobj)
            self.finished = True
        if self.finished == True:sys.exit()

class Conf():
    def __init__(self):
        self.conf = {}
        self.conf['pairwisetest'] = False
        self.conf['combination'] = False
        self.conf['whitelist'] = []
        self.conf['blacklist'] = []
        self.conf['batch'] = 50
        self.conf['getobjfromnet'] = False
        self.conf['specialapi'] = []

    def load(self,path):
        file = open(path,encoding='gbk')
        dictinsertdict(yaml.load(file),self.conf)
        file.close()
        return self.conf

def registctrlc(callback):
    signal.signal(signal.SIGINT,callback)

if __name__ == "__main__":
    ymlpath = '%s%sconf.yml' % (os.path.split(os.path.realpath(__file__))[0], os.path.sep)
    userconfig = Conf().load(ymlpath)
    apiobj = apiload(userconfig['getobjfromnet'])
    mockserver = server(userconfig,apiobj)
    print('mock server start!')
    registctrlc(mockserver.stop)
    mockserver.start()
