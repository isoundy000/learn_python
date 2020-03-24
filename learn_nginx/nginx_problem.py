#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# 重启nginx时nginx -s reload，报错信息如下：
# nginx: [error] open() "/usr/local/var/run/nginx.pid" failed (2: No such file or directory)
# 原因:
# 没有nginx.pid 这个文件，每次当我们停止nginx时(nginx -s stop) ,nginx 会把 /usr/local/var/run/ 路径下名为nginx.pid 的文件删掉
# 可以直接启动nginx，重新生成nginx.pid就可以了：
# nginx
# 如果直接启动还是不可行，执行nginx -t查看nginx配置文件路径：
# nginx -t
# nginx: the configuration file /usr/local/etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /usr/local/etc/nginx/nginx.conf test is successful
# 指定一下conf文件：
# nginx -c /usr/local/etc/nginx/nginx.conf
# 再次重启nginx -s reload，就不会报错了。