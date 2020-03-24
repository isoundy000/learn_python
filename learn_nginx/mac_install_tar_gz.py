#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


# mac pro nginx配置
# 1，下载pcre包pcre-8.12.tar.gz
# sudo tar xvfz pcre-8.12.tar.gz  解压文件
# 解压完成之后，执行命令
# cd pcre-8.12
# sudo ./configure --prefix=/usr/local --enable-utf8
# sudo make
# sudo make install
# 2，下载nginx
# tar xvzf nginx-1.2.0.tar.gz
# cd nginx-1.2.0
# sudo ./configure --prefix=/usr/local/nginx --with-http_ssl_module
# sudo make
# sudo make install
# 3，配置nginx命令
# vim ~/bash_profile
# # nginx
# NGINX_BIN=/usr/local/nginx/sbin
# PATH=$NGINX_BIN:$PATH


# server {
#     listen 80;
#     server_name 127.0.0.1;
#     location / {
#         alias /Users/noahli/workspace/collect/jxl_collect_i1/www/;
#         expires 1d;
#     }
#
#     location /orgApi/ {
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#         proxy_set_header REMOTE-HOST $remote_addr;
#         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504 http_404;
#         proxy_pass https://www.juxinli.com/orgApi/;
#         proxy_redirect default;
#     }
# }

# 4，nginx命令
# 重启:nginx -s reload
# 停止：nginx -s stop