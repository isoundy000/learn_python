#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# SSH连接报错:Permission denied, please try again.的解决方法
#   近期在做Linux下tomcat自启动的时候,ssh连接服务器的时候报错:

# Permission denied, please try again.如下报错
# 当使用 SSH 登录云服务器 ECS （Elastic Compute Server） Linux 服务器时，如果是 root 用户，即便正确输入了密码，也会出现类似如下错误信息。
#     Permission denied, please try again.
#     SSH 服务器拒绝了密码，请再试一次。
# 但非root用户可以正常登录，而且root用户通过 管理终端 登录也正常。
# 服务端SSH 服务配置了禁止root用户登录策略。
# 说明：相关策略可以提高服务器的安全性。请用户基于安全性和易用性权衡后，再确定是否需要修改相关配置。
# 要解决此问题，请进行如下配置检查和修改：
# 1 通过 管理终端 进入系统。
# 2 通过 cat 等指令查看 /etc/ssh/sshd_config 中是否包含类似如下配置：
# PermitRootLogin no

# 1 参数说明：
# 未配置该参数，或者将参数值配置为 yes （默认情况），都允许 root 用户登录。只有显示的设置为 no 时，才会阻断root 用户登录。
# 该参数只会影响用户的 SSH 登录，不影响用户通过 管理终端 等其它方式登录系统。
# 2 使用 vi 等编辑器，将参数值设置为 yes，或者整个删除或注释（在最开头添加 # 号）整行配置。比如：
#  PermitRootLogin yes
# 3 # PermitRootLogin no
# 4 使用如下指令重启 SSH 服务：
# service sshd restart