# -*- encoding: utf-8 -*-
'''
Created on 2017年8月6日

@author: houguangdong
'''
# XML
# XML虽然比JSON复杂，在Web中应用也不如以前多了，不过仍有很多地方在用，所以，有必要了解如何操作XML。
# DOM vs SAX
# 操作XML有两种方法：DOM和SAX。DOM会把整个XML读入内存，解析为树，因此占用内存大，解析慢，优点是可以任意遍历树的节点。SAX是流模式，边读边解析，占用内存小，解析快，缺点是我们需要自己处理事件。
# 正常情况下，优先考虑SAX，因为DOM实在太占内存。
# 在Python中使用SAX解析XML非常简洁，通常我们关心的事件是start_element，end_element和char_data，准备好这3个函数，然后就可以解析xml了。
# 举个例子，当SAX解析器读到一个节点时：
# <a href="/">python</a>
# 会产生3个事件：
# start_element事件，在读取<a href="/">时；
# char_data事件，在读取python时；
# end_element事件，在读取</a>时。
# 用代码实验一下：

from xml.parsers.expat import ParserCreate

class DefaultSaxHandler(object):
    def start_element(self, name, attrs):
        print('sax:start_element: %s, attrs: %s' % (name, str(attrs)))

    def end_element(self, name):
        print('sax:end_element: %s' % name)

    def char_data(self, text):
        print('sax:char_data: %s' % text)

xml = r'''<?xml version="1.0"?>
<ol>
    <li><a href="/python">Python</a></li>
    <li><a href="/ruby">Ruby</a></li>
</ol>
'''
handler = DefaultSaxHandler()
parser = ParserCreate()
parser.returns_unicode = True
parser.StartElementHandler = handler.start_element
parser.EndElementHandler = handler.end_element
parser.CharacterDataHandler = handler.char_data
parser.Parse(xml)
# 当设置returns_unicode为True时，返回的所有element名称和char_data都是unicode，处理国际化更方便。
# 需要注意的是读取一大段字符串时，CharacterDataHandler可能被多次调用，所以需要自己保存起来，在EndElementHandler里面再合并。
# 除了解析XML外，如何生成XML呢？99%的情况下需要生成的XML结构都是非常简单的，因此，最简单也是最有效的生成XML的方法是拼接字符串：
L = []
L.append(r'<?xml version="1.0"?>')
L.append(r'<root>')
L.append(str.encode('some & data'))
L.append(r'</root>')
print ''.join(L)
# return ''.join(L)
# 如果要生成复杂的XML呢？建议你不要用XML，改成JSON。
# 小结
# 解析XML时，注意找出自己感兴趣的节点，响应事件时，把节点数据保存起来。解析完毕后，就可以处理数据。
# 练习一下解析Yahoo的XML格式的天气预报，获取当天和最近几天的天气：
# http://weather.yahooapis.com/forecastrss?u=c&w=2151330
# 参数w是城市代码，要查询某个城市代码，可以在weather.yahoo.com搜索城市，浏览器地址栏的URL就包含城市代码。


# 佛山天气,并将当天数据放在一个list里
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib  #用来抓去网站信息的模块
from xml.parsers.expat import ParserCreate  #解析器
import re  #正则表达式

try:
    #创建链接实例,获取百度天气API
    page = urllib.urlopen('http://api.map.baidu.com/telematics/v2/weather?location=%E4%BD%9B%E5%B1%B1&ak=B8aced94da0b345579f481a1294c9094')
    #读取实例内容,赋值给XML
    XML = page.read()
finally:
    page.close() #不能使用with as,貌似实例没有__exit__

a = re.compile(r'^\s+$')  #空格,正则表达式

class BaiduWeatherSaxHandler(object):
    def __init__(self):
        self.L = []  #创建一个list装XML中的关键数据
        self.R = False   #当start_element获得的name与
        self.d = ['currentCity','date','weather','wind','temperature']
    def start_element(self,name,attrs):
        # print ('sax:start_element:%s,attrs:%s' % (name,str(attrs)))
        if name in self.d:
            self.R = True
    def end_element(self, name):
        # print ('sax:end_element: %s' % name)
        if name == 'result':  #只让程序显示当天的天气(API中还有未来几天的)
            for x in self.L:
                print x
            raise SystemExit  #关闭程序

    def char_data(self, text):

        if a.match(text):  #去掉空格的(没内容的)
            pass
        elif self.R:
            self.L.append(text)
            self.R = False
        # else:
        #     print ('sax:char_data: %s' % text)

handler =BaiduWeatherSaxHandler()  #设置解析方法
parser =ParserCreate()  #创建解析器
# 设置解析器参数
parser.returns_unicode = True  #返回unicode编码
parser.StartElementHandler = handler.start_element
parser.EndElementHandler = handler.end_element
parser.CharacterDataHandler = handler.char_data
parser.Parse(XML)  #解析文本

# ==============================================================

import urllib
from xml.parsers.expat import ParserCreate
import re
# 解析天气预报
# 百度天气
xml = ''
try:
    page = urllib.urlopen('http://api.map.baidu.com/telematics/v2/weather?location=%E4%B8%8A%E6%B5%B7&ak=B8aced94da0b345579f481a1294c9094')
    xml = page.read()
finally:
    page.close()
# print xml


class BaiduWeatherSaxHandler(object):
    def __init__(self):
        self._weather = dict()
        self._count = 0
        self._current_element = ''

    def start_element(self, name, attrs):
        if name == 'result':
            self._count += 1
            self._weather[self._count] = dict()
        self._current_element = name

    def end_element(self, name):
        pass

    def char_data(self, text):
        # 排除换行符和空白内容
        re_str = '^[\n|\s]+$'
        if self._current_element and not re.match(re_str, text) and self._weather:
            self._weather[self._count][self._current_element] = text

    def show_weather(self):
        for v in self._weather.values():
            print v['date'], '\t'*(7-len(v['date'])), v['temperature'], v['weather'], v['wind']

handler = BaiduWeatherSaxHandler()
parser = ParserCreate()

parser.returns_unicode = True
parser.StartElementHandler = handler.start_element
parser.EndElementHandler = handler.end_element
parser.CharacterDataHandler = handler.char_data

parser.Parse(xml)

handler.show_weather()
# 百度是信息放在characterdata里的，还有一种放在attrs里的可以自己试试
# url = 'http://flash.weather.com.cn/wmaps/xml/china.xml'
