# -*- coding: utf-8 -*-
import hashlib
import urllib
from pandas import json


def trans_baidu(src):
    ApiKey = "SCcYBOTQZKUldcMpzdCl"  # 百度开发者apikey
    ApiID = '20160429000019908'
    salt = '1435660288'
    print(src)
    srcstr = ApiID + src + salt + ApiKey
    print(srcstr)
    srcstr = srcstr.encode('utf-8')
    print(srcstr)
    m = hashlib.md5()
    m.update(srcstr)
    sign = m.hexdigest()
    params = urllib.parse.urlencode({'q': src})
    turl = "http://api.fanyi.baidu.com/api/trans/vip/translate?" + params + "&from=en&to=zh&appid=" + ApiID + "&salt=" + salt + "&sign=" + sign
    print(turl)

    try:
        f = urllib.request.urlopen(turl)
        con = f.read()
    except:
        print('raise e')
    else:
        decoded = json.loads(con)
        dst = decoded["trans_result"][0]["dst"].encode('utf-8')
        return dst
