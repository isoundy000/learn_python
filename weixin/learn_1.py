# -*- encoding: utf-8 -*-
'''
Created on 2017年8月30日

@author: houguangdong
'''
# 1 可变数据类型作为函数定义中的默认参数
def fn(var1, var2=[]):
    var2.append(var1)
    print var2

  
def fn1(var1, var2=None):
    if not var2:
        var2 = []
    var2.append(var1)
    print var2


fn(3)
fn(4)
fn(5)
fn1(6)
fn1(7)
fn1(8)


# 2 可变数据类型作为类变量
class URLCatcher(object):
    urls = []
    def add_url(self, url):
        self.urls.append(url)


a = URLCatcher()
a.add_url("http://www.google.com")
b = URLCatcher()
b.add_url("http://www.baidu.com")
print a.urls
print b.urls


class URLCatcher1(object):
    def __init__(self):
        self.urls = []
    
    def add_url(self, url):
        self.urls.append(url)

a = URLCatcher1()
a.add_url("http://www.google.com")
b = URLCatcher1()
b.add_url("http://www.baidu.com")
print a.urls
print b.urls


# 3 可变的分配错误
a = {"1": "one", "2": "two"}
b = a
b["3"] = "three"
print a, b


c = (2, 3)
d = c
d = (4, 5)
print c, d