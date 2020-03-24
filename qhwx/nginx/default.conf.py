#!/usr/bin/env python
# -*- coding:utf-8 -*-
# upstream django {
#     server 127.0.0.1:9090;
# }
#
# server {
#     listen       8000 default_server;
#     listen       [::]:8000 default_server;
#     server_name  127.0.0.1;
#     root         /usr/share/nginx/html;
#
#     location / {
#         uwsgi_pass django;
#         include uwsgi_params;
#     }
#
#     location /static/ {
#         alias /root/PycharmProjects/jpzmg/static/;
#     }
# }