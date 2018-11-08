# -*- encoding: utf-8 -*-
'''
Created on 2018年10月19日

@author: houguangdong
'''


import requests
import urllib3
import json
import urllib
# from urllib import request
from bs4 import BeautifulSoup

xba = None
for i in range(1, 15):
    url1 = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv4403&productId=3487485&score=3&sortType=5&page='
    url2 = str(i)
    uel3 = '&pageSize=10&isShadowSku=0&rid=0&fold=1'
    finalurl = url1 + url2 + uel3
    print finalurl
    xba = requests.get(finalurl)

for i in range(1, 15):
    u1 = "./pachong1/"
    u2 = str(i)
    u3 = ".json"
    finalu = u1 + u2 + u3
    file = open(finalu, "w")
    file.write(xba.text[26:-2])
    file.close()

st = xba.text
print('finished')


# 3再定个中等目标，爬取150页用户具体评论内容，并存入本地
for i in range(1, 150):
    url1 = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv4403&productId=3487485&score=3&sortType=5&page='
    url2 = str(i)
    url3 = '&pageSize=10&isShadowSku=0&rid=0&fold=1'
    finalurl = url1 + url2 + url3
    xba = requests.get(finalurl)
    data = json.loads(xba.text[26:-2])
    for i in data['comments']:
        content = i['content']
        print("评论内容".format(content))
        file = open("./pachong1/comm.txt", 'a')
        file.writelines(format(content))

print('finished')