#!/usr/bin/env python
# -*- coding:utf-8 -*-
# （一）django有四中session实现方式
# 1、数据库(database-backed sessions)
# 2、缓存（cached sessions）
# 3、文件系统（file-based sessions）
# 4、cookie(cookie-based sessions)
#
# 其中数据库方式是默认的也是默认就启用的，其实现方式实际上是通过django中间件实现的，配置在INSTALLED_APPS中的django.contrib.sessions。目前先使用数据库方式的session，其他以后继续补充，首先考虑改进为“缓存”。
#
# （二）django session使用基础
# 1、存放数据到session
# request.session['some_id'] = some_id
# 2、从session中读取存放的数据
# session.get('some_id', False)
# 3、从session中将数据删除
# del request.session['some_id']
# 4、让session过期
# request.session.set_expiry()
# 5、在命令行访问sessin数据
# # 生成并保存session（利用SessionStore）
# from django.contrib.sessions.backends.db import SessionStore
# sessionStore = SessionStore()
# sessionStore["str"] = "hello"                  #  字串映射
# sessionStore["dict"] = {};                     #  可以定义多级的字典结构
# sessionStore["dict"]["key1"]="value1"
# sessionStore["dict"]["key2"]="value2"
# sessionStore.save();
# print(sessionStore.session_key);
# print(sessionStore.keys());
# session_key = sessionStore.session_key;
# # 读取保存的session
# from django.contrib.sessions.models import Session
# session = Session.objects.get(pk=session_key)
# print(session.session_data);                 # 返回session的存储（加密过）
# print(session.get_decoded());                # 返回session的数据结构（加过解码）
# print(session.expire_date);
# 注意：
# （1）保存数据的使用使用的是SessionStore读取数据使用使用的是Session。
# （2）在使用多级字典时session["dict"]["key1"] = "something" django默认不会对多级对象进行保存，需要显示的使用代码 request.session.modified = True 。
#
# （三）Session的重要配置参数(在setting.py中配置)
# 1、SESSION_SAVE_EVERY_REQUEST
# 如果设置为True,django为每次request请求都保存session的内容，默认为False。
# 2、SESSION_EXPIRE_AT_BROWSER_CLOSE
# 如果设置为True，浏览器已关闭session就过期了，默认为False。
# 3、SESSION_COOKIE_AGE
# 设置SESSION的过期时间，单位是秒，默认是两周