#!/usr/bin/env python
# -*- coding:utf-8 -*-

# django项目搭建与Session使用详解
# 前言
# Django完全支持也匿名会话，简单说就是使用跨网页之间可以进行通讯，比如显示用户名，用户是否已经发表评论。session框架让你存储和获取访问者的数据信息，这些信息保存在服务器上（默认是数据库中），以 cookies 的方式发送和获取一个包含 session ID的值，并不是用cookies传递数据本身。
# 本文给大家详细介绍了关于django项目搭建与Session使用的相关内容，分享出来供大家参考学习，下面话不多说了，来一起看看详细的介绍吧
# django+session+中间件
# 配置session
# django的session可以分为内存缓存存储、文件存储、数据库存储。这里我们采用数据库存储。
# django项目默认是开启session的，默认存储方式为：SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# （本地缓存：SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# 混合缓存：SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'）
# 当然也可以是redis缓存：
#
# CACHES = {"default": {"BACKEND": "django_redis.cache.RedisCache", "LOCATION": "redis://ip:端口/",
#                       "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient", }}}
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"
# 我们这里使用django自带的sqlite存储session，settings配置如下：
# SESSION_COOKIE_SECURE = False
# SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_NAME = 'xxxx'
# SEESION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_COOKIE_AGE = 18000
# 这里的设定的时间作用不大，可以直接在代码里指定时间：request.session.set_expiry(0) 参数0代表退出浏览器session即失效，单位均为毫秒
# 中间件MIDDLEWARE_CLASSES中查看是否有'django.contrib.sessions.middleware.SessionMiddleware' 没有的话添加即可
# 这里我们已经设置好了django session的环境，我们需要使用django自带的模块处理session值
# 这里需要强调一点，用sqlite数据库存储session需要初始化下数据库，在manage.py文件所在目录下执行命令：
# python manage.py makemigrations（python manage.py migrate）
# 至此，session准备工作已经完成。但是需要注意的是session失效，只是时间上失效，其值还是存在库中，因此需要定期删除，也可以在代码中逻辑删除，具体代码如下：
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import datetime
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session


def delsession(key):
    if key is None:
        return
    store = SessionStore()
    store.delete(key)

count = Session.objects.all().count()
if count > 20:
    nowtime = datetime.datetime.now()
    outdatesession = Session.objects.filter(expire_date__lt=nowtime)
    for item in outdatesession:
        store.delete(item.session_key)


def delovertimesession():
    store = SessionStore()


count = Session.objects.all().count()
if count > 20:
    nowtime = datetime.datetime.now()
    outdatesession = Session.objects.filter(expire_date__lt=nowtime)
    for item in outdatesession:
        store.delete(item.session_key)

# 三、请求的中间件
# 安全认证、请求过滤以及session的初始值 我们可以在中间件中处理。
# 在djangocommon项目下，新增middlehttp.py文件，代码大致如下：
reload(sys)
sys.setdefaultencoding('utf-8')

from django.shortcuts import render_to_response


# process_request -------- 接受request之后确定view之前执行
# process_view 确定view之后 并且在view真正执行之前执行
# process_response view执行之后
# process_exception(self, request, exception) view抛出异常

class LoginRequiredMiddleware:
    def process_request(self, request):
        path = request.path_info.strip('/')
        # 这里写处理逻辑和请求控制

# 在settings文件中的中间件配置MIDDLEWARE_CLASSES中添加'djangocommon.middlehttp.LoginRequiredMiddleware' 如下：
# MIDDLEWARE_CLASSES = [
#  'django.middleware.security.SecurityMiddleware',
#  'django.contrib.sessions.middleware.SessionMiddleware',
#  'django.middleware.common.CommonMiddleware',
#  'django.middleware.csrf.CsrfViewMiddleware',
#  'django.contrib.auth.middleware.AuthenticationMiddleware',
#  'django.contrib.auth.middleware.SessionAuthenticationMiddleware',　　 'djangocommon.middlehttp.LoginRequiredMiddleware',
#  'django.contrib.messages.middleware.MessageMiddleware',
#  'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]
# 注意顺序，必须在SessionMiddleware之后。
# 至此，一个完整的django+session+中间件 项目搭建完成。前后端分离的项目，也可以以此为基础，通过webpack或cli 搭建 编译生成的templates及静态文件即可。