#!/usr/bin/env python
# -*- coding:utf-8 -*-

from hashlib import md5

import urllib
import time
import datetime
import re

import settings

from admin.admin_models import Admin
import admin_config


def build_auth_signature(auth_fields):
    """生成auth签名"""
    payload = '&'.join(k + "=" + str(auth_fields[k]) for k in sorted(auth_fields.keys()) if k != "auth_fields")

    return md5(payload).hexdigest()


def force_str(text, encoding="utf-8", errors='strict'):
    t_type = type(text)
    if t_type == str:
        return text
    elif t_type == unicode:
        return text.encode(encoding, errors)
    return str(text)


def force_unicode(text, encoding="utf-8", errors='strict'):
    t_type = type(text)
    if t_type == str:
        return text.decode(encoding, errors)
    elif t_type == unicode:
        return text
    elif hasattr(text, '__unicode__'):
        return unicode(text)
    return unicode(str(text), encoding, errors)


def get_hexdigest(raw_str):
    return md5(raw_str).hexdigest()


def check_password(raw_password, enc_password):
    return get_hexdigest(raw_password) == enc_password


def login(request, admin):
    """
    管理员登陆
    """
    login_time = datetime.datetime.now()
    login_ip = request.request.headers.get('X-Real-Ip', '')
    admin.set_last_login(login_time, login_ip)
    # admin.put()
    username = admin.username

    last_login_stamp = time.mktime(admin.last_login.timetuple())
    token = build_auth_signature({
        "username": username,
        "last_login": last_login_stamp,
        "secret_key": 'fuck',
    })
    cv = "%s|%s|%s" % (username, last_login_stamp, token)
    cv = urllib.quote(cv.encode("ascii"))
    admin.save()
    request.set_cookie("kqqadmin", cv)


def logout(request):
    request.clear_cookie("kqqadmin")


def get_admin_by_request(request):
    "通过request获取admin"
    cv = request.get_cookie("kqqadmin")
    # print cv, type(cv)
    if cv is None:
        return None
    else:
        cv = urllib.unquote(cv).decode("ascii")
        mid, login_stamp, token = cv.split('|')
        # print mid
        admin = Admin.get(mid)
        if admin is None:
            return None

        raw_last_login_stamp = time.mktime(admin.last_login.timetuple())
        new_token = build_auth_signature({
            "username": mid,
            "last_login": raw_last_login_stamp,
            "secret_key": 'fuck'
        })
        if new_token == token:
            return admin
        return None


def get_menu():
    result = []
    href_dict = admin_config.left_href
    for item in href_dict:
        value = item
        name = force_unicode(href_dict[item]['name'])
        result.append((value, name))
    return result


def has_left_view(path, left_href_list, right_links):
    if left_href_list:
        # 基础页面 直接通过
        for key in admin_config.base_page_list:
            if path in key:
                return True

        for key in left_href_list:
            if path in admin_config.left_href[key]['path']:
                return True

        for key in right_links:
            if key in path:
                return True

    return False

# 后台调用进行创建账户接口
def make_admin_user(username, password, setnx=True):
    """
    给定用户名和密码直接创建管理用户, 参数都是字符串类型
    """
    admin = Admin.get(username)
    if admin:
        flag = 0
        left_href_list = admin_config.get_all_href_key()
        right_links = admin_config.secondary_links.keys()
        if admin.left_href_list != left_href_list:
            for i in left_href_list:
                if i not in admin.left_href_list:
                    admin.left_href_list.append(i)
            flag = 1
        if admin.right_links != right_links:
            if not isinstance(admin.right_links, list):
                admin.right_links = []
            for i in right_links:
                if i not in admin.right_links:
                    admin.right_links.append(i)
            flag = 1
        if flag:
            admin.save()
        return

    if not setnx:
        return
    admin = Admin()
    admin.username = username
    admin.password = password
    admin.left_href_list = admin_config.get_all_href_key()
    admin.email = username + '@kaiqigu.com'
    admin.permissions = ""
    admin.right_links = admin_config.secondary_links.keys()
    admin.save()
    return admin


for username, password in settings.DEFAULT_BACKEND_ADMIN:
    make_admin_user(username, password)
for username in settings.DEFAULT_BACKEND_SUPER_ADMIN:
    make_admin_user(username, '', setnx=False)