#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# apache2下部署node.js应用程序

# 版本：apache2.2+node.js(v.10.25)
# 系统环境：ubuntu 12.04(LTS) 32位
# 因为有些模块并没有开启 所以需要使用以下命令开启该模块 windows下则直接在httpd.conf里面将LoadModule前面的#删除即可
# 在配置之前需要使用proxy模块以及proxy_http模块，执行以下命令：

# a2enmod proxy
# a2enmod proxy_http

# 然后重启apache
# 命令如下：

# service apache2 restart
# 找到/etc/apache2/sites-available/default.conf
# 打开
#
# 在<VituralHost>

# </VituralHost>中添加下面代码
#
#     ProxyRequests Off
#     <Proxy *>
#         Order deny,allow
#         Allow from all
#     </Proxy>
#     ProxyPreserveHost on
#
#     ProxyPass /node http://localhost:3000/article
#
# 接下来是为每一个页面中的css文件以及js文件添加代理地址 如果不添加代理的话 则这些文件是访问不到的
#
# 或者可以将这些文件放在apache的文件夹里面也是可以的
#
#  自己部署网站的时候遇到的一些问题 记录一下
