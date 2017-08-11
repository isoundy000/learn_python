# -*- encoding: utf-8 -*-
'''
Created on 2017年8月6日

@author: houguangdong
'''
# HTMLParser
# 如果我们要编写一个搜索引擎，第一步是用爬虫把目标网站的页面抓下来，第二步就是解析该HTML页面，看看里面的内容到底是新闻、图片还是视频。
# 假设第一步已经完成了，第二步应该如何解析HTML呢？
# HTML本质上是XML的子集，但是HTML的语法没有XML那么严格，所以不能用标准的DOM或SAX来解析HTML。
# 好在Python提供了HTMLParser来非常方便地解析HTML，只需简单几行代码：
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        print('<%s>' % tag)

    def handle_endtag(self, tag):
        print('</%s>' % tag)

    def handle_startendtag(self, tag, attrs):
        print('<%s/>' % tag)

    def handle_data(self, data):
        print('data')

    def handle_comment(self, data):
        print('<!-- -->')

    def handle_entityref(self, name):
        print('&%s;' % name)

    def handle_charref(self, name):
        print('&#%s;' % name)

parser = MyHTMLParser()
parser.feed('<html><head></head><body><p>Some <a href=\"#\">html</a> tutorial...<br>END</p></body></html>')
# feed()方法可以多次调用，也就是不一定一次把整个HTML字符串都塞进去，可以一部分一部分塞进去。
# 特殊字符有两种，一种是英文表示的&nbsp;，一种是数字表示的&#1234;，这两种字符都可以通过Parser解析出来。
# 小结
# 找一个网页，例如https://www.python.org/events/python-events/，用浏览器查看源码并复制，然后尝试解析一下HTML，输出Python官网发布的会议时间、名称和地点。



from HTMLParser import HTMLParser

class PyEventParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self._count = 0
        self._events = dict()
        self._flag = None

    def handle_starttag(self, tag, attrs):
        if tag == 'h3' and attrs.__contains__(('class', 'event-title')):
            self._count += 1
            self._events[self._count] = dict()
            self._flag = 'event-title'
        if tag == 'time':
            self._flag = 'time'
        if tag == 'span' and attrs.__contains__(('class', 'event-location')):
            self._flag = 'event-location'

    def handle_data(self, data):
        if self._flag == 'event-title':
            self._events[self._count][self._flag] = data
        if self._flag == 'time':
            self._events[self._count][self._flag] = data
        if self._flag == 'event-location':
            self._events[self._count][self._flag] = data
        self._flag = None

    def event_list(self):
        print '近期关于Python的会议有：', self._count, '个，具体如下：'
        for event in self._events.values():
            print event['event-title'], '\t', event['time'], '\t', event['event-location']


try:
    import urllib2
    parser = PyEventParser()
    pypage = urllib2.urlopen('https://www.python.org/events/python-events/')
    pyhtml = pypage.read()
except IOError,e:
    print 'IOError:', e
else:
    parser.feed(pyhtml)
    parser.event_list()
finally:
    pypage.close()
    
    




from HTMLParser import HTMLParser
import urllib

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.key = {'time': None, 'event-title': None, 'event-location': None}

    def handle_starttag(self, tag, attrs):
        if tag == 'time':
            self.key['time'] = True
        elif tag == 'span' and attrs.__contains__(('class', 'event-location')):
            self.key['event-location'] = True
        elif tag == 'h3' and attrs.__contains__(('class', 'event-title')):
            self.key['event-title'] = True

    def handle_data(self, data):
        if self.key['time']:
            print 'Time:%s\t|' % data,
            self.key['time'] = None
        elif self.key['event-title']:
            print 'Title:%s\t|' % data,
            self.key['event-title'] = None
        elif self.key['event-location']:
            print 'Location:%s\t|' % data
            self.key['event-location'] = None

parser = MyHTMLParser()
html = urllib.urlopen('http://www.python.org/events/python-events/').read()
parser.feed(html)




from pyquery import PyQuery
doc = PyQuery(url='https://www.python.org/events/python-events/')
for event in doc('.list-recent-events li'):
    event = PyQuery(event)
    loc = event.find('.event-location').text()
    time = event.find('time').text()
    name = event.find('.event-title').text()
    print 'event:%s' % name
    print '\ttime:%s' % time
    print '\tlocation:%s' % loc