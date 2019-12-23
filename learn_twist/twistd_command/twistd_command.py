#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/19 23:52
# @version: 0.0.1
# @Author: houguangdong
# @File: twistd_command.py
# @Software: PyCharm


# 我们可以像这样运行这个Echo服务应用：
# twistd –y echo_server.tac

# Twisted还带有一个可拔插的针对服务器端认证的模块twisted.cred，插件系统常见的用途就是为应用程序添加一个认证模式。我们可以使用twisted.cred中现成的AuthOptionMixin类来添加针对各种认证的命令行支持，或者是添加新的认证类型。比如，我们可以使用插件系统来添加基于本地Unix密码数据库或者是基于LDAP服务器的认证方式。
# twistd web --port 8080 --path .
# twistd/twist web
# 这条命令将在8080端口启动一个HTTP服务器，在当前目录中负责处理静态和动态页面请求。

# twistd dns –p 5553 –hosts-file=hosts
# twist dns -p 5555
# 这条命令在端口5553上启动一个DNS服务器，解析指定的文件hosts中的域名，这个文件的内容格式同/etc/hosts一样。


# twistd conch –p tcp:2222
# 这条命令在端口2222上启动一个SSH服务器。ssh的密钥必须独立设定

# twistd mail –E –H localhost –d localhost=emails
# 这条命令启动一个ESMTP POP3服务器，为本地主机接收邮件并保存到指定的emails目录下。


