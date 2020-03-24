#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# 使用 apache2 + `mod_proxy_uwsgi` + uwsgi + upstart 部署
# 使用 apache2 + mod_proxy_uwsgi + uwsgi + upstart 部署
# 网上运行 python wsgi 的应用时，大部分的资料都是使用 nginx 、uwsgi ，很少资料提及到 apache2 下如何进行处理。但是平时的部署环境其实很难跳过 apache2 ，很多环境已经带 apache2 ，不好另外安装一个 nginx ，因此，经过一番测试后，建议使用 apache2 + mode_proxy_uwsgi + uwsgi + upstart/systemd 的配置。整个配置并不复杂，请按照具体的步骤逐个处理。
# 以下的安装步骤是在 ubuntu 14.04 和 python3 中完成的。
# 安装依赖
# 安装 flask 和 uwsgi ::
# pip3 install flask
# pip3 install uwsgi
# 应用编写
# 首先，编写一个简单应用用于测试，可以使用 flask 或 django ，如果对 wsgi 熟悉，也可以直接使用 wsgi。这里是一个 flask 的示例 /var/www/test_app.py::

import flask
application = flask.Flask(__name__)

@application.route('/')
def index():
    return 'Hello, world!'

if __name__ == '__main__':
    application.run()

# 然后，做个简单的测试，启动服务器 ::
# python3 /var/www/test_app.py
# 打开一个新的终端，用 curl 请求 ::
# curl -v http://127.0.0.1:5000
# 可看到输出为 Hello, world!

# uwsgi 配置
# uwsgi 的运行方式有多种，这里只用命令行参数的方式运行，并写入到 upstart 中自动启动 /etc/init/uwsgi-test.conf ::
# description     "uwsgi test"
#
# start on runlevel [2345]
# stop on runlevel [!2345]
#
# env LC_ALL=zh_CN.UTF-8
# env LANG=zh_CN.UTF-8
# env PYTHONIOENCODING=utf-8
#
# exec uwsgi --socket 127.0.0.1:5000 --master --workers 2 --wsgi-file /var/www/test_app.py
#
# 为了能正确地处理 utf-8 编码的内容和日志输出，env 部分不能少。在 uwsgi 的配置可放到 ini 格式的配置文件中，并可指定一个 virtualenv 环境，防止破坏了主机的 python 环境，更多的配置选项见 http://uwsgi-docs.readthedocs.io/en/latest/
# 然后启动 uwsgi ::
# start uwsgi-test
#
# 安装和配置 apache2
#
# 在 ubuntu 中，安装 apache2 和相关的工具 ::
#
# apt-get install apache2 apache2-utils libapache2-mod-proxy-uwsgi
#
# 启用 mod_proxy_uwsgi ::
#
# a2enmod proxy
# a2enmod proxy_uwsgi
#
# 注意，必须同时启用 proxy 模块，否则 apache2 会报错，错误信息为 ::
#
# Cannot load /usr/lib/apache2/modules/mod_proxy_uwsgi.so into
# server: /usr/lib/apache2/modules/mod_proxy_uwsgi.so:
# undefined symbol: ap_proxy_backend_broke。
#
# 编写一个配置文件 test.conf 放在 /etc/apache2/conf-available ::
#
# ProxyPass /test uwsgi://127.0.0.1:5000
#
# 启用配置文件
#
# a2enconf test
#
# 并重启 apache2 ::
#
# service apache2 restart
#
# 现在用 curl 测试一下 ::
#
# curl -v http://127.0.0.1/test
#
# 可看到输出为 Hello, world! 。
#
# 至此，全部工作已完成。