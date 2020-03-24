#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


# server {
#     listen       21374 default_server;
#     listen       [::]:21374 default_server;
#     server_name  127.0.0.1;
#     root         /usr/share/nginx/html;
#
#     #location / {
#     #    proxy_pass http://127.0.0.1:8844;
#     #    proxy_set_header   Host    $host;
#     #    proxy_set_header   X-Real-IP   $remote_addr;
#     #    proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
#     #}
#
#     location /acc_account {
#         proxy_set_header   Host    $host;
#         proxy_set_header   X-Real-IP   $remote_addr;
#         proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_pass http://127.0.0.1:9002;
#     }
#
#     location /boss {
#         rewrite /boss/(.*) /$1 break;
#         proxy_pass http://127.0.0.1:8848;
#         proxy_set_header   Host    $host;
#         proxy_set_header   X-Real-IP   $remote_addr;
#         proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
#     }
#
#     location /monitor {
#         rewrite /monitor/(.*) /$1 break;
#         proxy_pass http://127.0.0.1:53492;
#         proxy_set_header   Host    $host;
#         proxy_set_header   X-Real-IP   $remote_addr;
#         proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
#     }
#
#     location /rank_server {
#         rewrite /rank_server/(.*) /$1 break;
#         proxy_pass http://127.0.0.1:13253;
#         proxy_set_header   Host    $host;
#         proxy_set_header   X-Real-IP   $remote_addr;
#         proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
#     }
#
#     location /game_servers {
#         proxy_set_header   Host    $host;
#         proxy_set_header   X-Real-IP   $remote_addr;
#         proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
#         proxy_pass http://127.0.0.1:2222;
#     }
# }