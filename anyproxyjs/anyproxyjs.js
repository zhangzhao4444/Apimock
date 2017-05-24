
// @author: zhangzhao_lenovo@126.com
// @date: 20161125
// @version: 1.0.0.1034

//rule scheme :
//npm install iconv-lite
var iconv = require('iconv-lite');
var url = require("url");
var net = require('net');

var server = '127.0.0.1';
var port = 8390;
var host = "u.panda.tv";
//var host = "www.3663.com";
var code = 200;
var flag = 0;

module.exports = {
     shouldInterceptHttpsReq :function(req){
         return true;
    },

    replaceServerResDataAsync: function(req,res,serverResData,callback){
        if(req.headers.host == host && res.statusCode == "200"){
            var charset = 'utf-8', charsetMatches = res.headers['content-type'].match(/;\s*charset=(.+)/i);
            if(charsetMatches){charset = charsetMatches[1];}
            var body = iconv.decode(serverResData,charset);
            var jquery = body.match(/jQuery(.*)/i);
		    if (jquery) {var rawbody = body.match(/(\{.*\})/g);
		    }else{var rawbody = body;}
            var mockbody = '';
            try{
                var j = JSON.parse(rawbody);
                if (typeof(j) == "object" && Object.prototype.toString.call(j).toLowerCase() == "[object object]" && !j.length) {
                    var api = url.parse(req.url).pathname;
                    rawbody = api + ':' + rawbody;
                    var client = new net.Socket();
                    client.connect(port, server,function() {
                        client.write(rawbody);
                    });
                    client.on('data',function (buf) {
                        mockbody = buf.toString();
                        client.destroy();
                    });
                    client.on('close', function() {
                        rawbody = mockbody;
                        try{
                            var j = JSON.parse(mockbody);
                            if (typeof(j) == "object" && Object.prototype.toString.call(j).toLowerCase() == "[object object]" && !j.length) {
                                if (j['mock']['responsecode'] == '200') {
                                    delete j['mock'];
                                }else{
                                    flag = 1;
                                    code = parseInt(j['mock']['responsecode']);
                                }
                                rawbody = JSON.stringify(j);
                            }
                            console.info(rawbody);
                        }catch(err){
                        }finally{
                            rawbody = iconv.encode(rawbody, charset);
                            callback(rawbody);
                        }
                    });
                }
            }catch(err){
                rawbody = iconv.encode(rawbody, charset);
                callback(rawbody);
            }
        }else{
            callback(serverResData);
        }
    },

    // replaceResponseStatusCode: function(req,res,statusCode){
    //     if(req.headers.host == host && flag == 1){
    //         statusCode = code;
    //     }
    //     return statusCode;
    // },
};
