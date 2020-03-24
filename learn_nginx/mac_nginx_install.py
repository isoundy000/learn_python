#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# https://blog.csdn.net/guo_qiangqiang
# https://blog.csdn.net/guo_qiangqiang/article/details/104211279

# MacBook Pro上安装Nginx详细教程
# 1. 安装（可以用 brew 安装）
# sudo brew install nginx
# 2. 查看 nginx 版本
# nginx -v
# 3. 启动 nginx
# sudo nginx
# 也可以使用下面的命令启动，但是配置文件nginx.conf修改后用这个命令执行不生效，故不建议使用：
# sudo brew services start nginx
# brew services restart nginx
# 4. 查看 nginx 是否启动成功
# 在浏览器中访问 http://localhost:8080，如果出现如下界面，则说明启动成功.
# 备注：端口号是在配置文件 nginx.conf 里面配置的，默认端口是 8080 ，配置文件的位置 /usr/local/etc/nginx
# 5. 关闭nginx
# sudo nginx -s stop
# 也可以使用下面的命令启动，但是配置文件nginx.conf修改后用这个命令执行不生效，故不建议使用：
# sudo brew services stop nginx
# 6. 重新加载nginx
# sudo nginx -s reload
# 7. 可能遇到的问题
# 端口被占用
# nginx: [emerg] bind() to 0.0.0.0:80 failed (48: Address already in use)
# 解决方法：修改 nginx.conf 文件里的端口号
# 权限不够
# nginx: [alert] could not open error log file: open() “/usr/local/var/log/nginx/error.log” failed (13: Permission denied)
# 解决方法：在命令前加上 sudo，这时可能会要求输入密码，密码就是电脑的开机密码啦~
# 8. 补充
# 安装 homebrew ，将以上命令粘贴至terminal，然后回车即可
# /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
# 常用的指令有：
# nginx -s reload 重新加载配置
# nginx -s reopen 重启
# nginx -s stop 停止
# nginx -s quit 退出
# nginx -V 查看版本，以及配置文件地址
# nginx -v 查看版本
# nginx -c filename 指定配置文件
# nginx -h 帮助
# 参考地址：
# https://brew.sh/index_zh-cn.html