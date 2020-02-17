#!/usr/bin/env python
# -*- coding:utf-8 -*-

from gevent import monkey
monkey.patch_all()

import os, sys
import signal
import psutil
import socket
import time
import datetime
import traceback
import gevent
from gevent.server import StreamServer
from gevent.pool import Pool

import settings
env = sys.argv[1]
server_name = sys.argv[2]
settings.set_evn(env, server_name)          # (dev_new, 1)
settings.ENVPROCS = 'chat'

from lib.utils.debug import print_log
from chat.client import Client, ClientManager
from chat.content import ContentFactory
from lib.utils.encoding import force_unicode, force_str
from logics.user import User

from tornado.options import define, options

# HOST = settings.SERVERS[settings.SERVICE_NAME]['chat_ip']
PORT = settings.SERVERS[[s for s in settings.SERVERS if s != 'master'][0]]['chat_port']

# 简单获取本机ip
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostbyname('www.baidu.com'), 80))
HOST = s.getsockname()[0]
s.close()

# HOST = '192.168.1.100'
# define("port", default=9999, help="run on the given port", type=int)
# options.parse_command_line()


POOLNUM = 1000
BUFFSIZE = 128 * 2
MAX_BUFFER_SIZE = 1024 * 4
messages_cache = {}             # 缓存最近 几条对话
MESSAGE_CACHE_SIZE = 50         # 缓存对话 数量


GAG_UIDS = ['g144057667', 'g180144322', 'g329553371',
            'g115446730', 'g306215001', 'g3007511836']      # 禁言的uid


GAG_MSG_SWITCH = False


def get_default_msg():
    return '<xml><length>359</length><content>{"inputStr": "尊敬的英雄们：近期因为聊天服务器出现故障，导致部分捣乱分子可以通过非法手段冒名其他英雄发送聊天消息，我们正在紧急修复。修复期间暂时关停聊天服务器，对您造成的不便我们深表歉意。","data":{},"dsign":"1430753055","avatarID":"1","vip":0,"level":1,"kqgFlag":"system"}</content></xml>'


process = psutil.Process(os.getpid())


def get_datetime_str():
    return time.strftime('%F %T')


client_manager = ClientManager()
content_factory = ContentFactory(settings.AD_CLICK)


def request_handler(client_socket, addr):

    global messages_cache

    now = int(time.time())
    client = Client(client_socket)
    client_manager.add_client(client)

    client_manager.lose_time_out_clients(now)

    print_log('[%s]' % get_datetime_str(), 'connected from %s:%s' % addr, 'client_socked_fd:', client.fileno)
    print_log('clients_num :', client_manager.get_client_count())

    while True:
        try:
            data = client_socket.recv(BUFFSIZE)
        except:
            client_manager.lose_client(client)
            break

        if not data:
            print_log('[%s]' % get_datetime_str(), 'client %s:%s disconnected' % addr, 'flag: %s, %s' % (data, type(data)))
            client_manager.lose_client(client)
            print_log('clients_num :', client_manager.get_client_count())
            break

        if data.strip().lower() == 'check':
            now = int(time.time())
            client_socket.sendall(str(process.get_memory_info()) + '|')
            client_socket.sendall('\nclients_num : %s;' % client_manager.get_client_count())
            client_socket.sendall('\nper_client_connect_time: "[(fileno, uid, game_id, '
                                  'guild_id, server_name, vip, domain, team_id, live_time)]--> %s";' %
                                  str(sorted([(x, y.uid, y.game_id, y.guild_id, y.server_name,
                                               y.vip, y.domain, y.team_id, now - y.ttl)
                                              for x, y in client_manager._clients.iteritems()],
                                              key=lambda x: x[1], reverse=True)))
            client_socket.sendall('\n')
            continue

        if data.strip().lower() == 'check_contents':
            client_socket.sendall(str(process.get_memory_info()) + '|' + str(id(content_factory)))
            client_socket.sendall('\ncontents : %s;' % repr([content.__dict__ for content in content_factory._contents.itervalues()]))
            client_socket.sendall('\n')
            continue

        if data.strip().lower() == 'quit':
            client_manager.lose_client(client)
            break

        # buffer超了指定大小还未找到规定格式的数据，主动断开连接
        if len(client.buffer) >= MAX_BUFFER_SIZE:
            client_manager.lose_client(client)
            break

        info = client.parse(data)

        if not info:
            continue

        tp = info['kqgFlag']
        if tp == 'first':
            try:
                u = User.get(info.get('uid'))
            except:
                client_manager.lose_client(client)
                break

            # if u.session_expired(info.get('ks')) or (u.device_mark and u.device_mark != info.get('device_mark'))\
            #         or (u.device_mem and u.device_mem != info.get('device_mem')):
            #     client_manager.lose_client(client)
            #     continue

            if u.is_ban:
                client_manager.lose_client(client)
                break

            client.init_info(info.get('uid'), info.get('association_id', ''),
                             info.get('game_id', ''), info.get('vip', 0),
                             info.get('domain', ''), info.get('team_id', ''),
                             addr[0], info.get('sid'), info.get('device_mark'), info.get('device_mem'))

            client_manager.add_server_client(client)
            # if client.vip >= 8:
            #     receivers_vip = []
            #     for _fd, _client in client_manager.get_client_by_server_name(client.server_name).items():
            #         if _fd != client.fileno:
            #             receivers_vip.append(gevent.spawn(_client.socket.sendall, client.msg))
            #     gevent.joinall(receivers_vip)
            #
            #     content = content_factory.get(content_factory.MAPPINGS['world'], client.server_name)
            #     content.add(client.msg)
            if GAG_MSG_SWITCH:
                client.socket.sendall(force_str(get_default_msg()))

            if not GAG_MSG_SWITCH:
                content = content_factory.get(content_factory.MAPPINGS['world'], client.server_name)
                msgs = content.show()
                if msgs:
                    client.socket.sendall(''.join(msgs))

                content_friend = content_factory.get(content_factory.MAPPINGS['friend'], client.server_name, client.uid)
                msgs = content_friend.get(client.uid)
                content_factory.delete(content_factory.MAPPINGS['friend'], client.server_name, client.uid)
                if msgs:
                    client.socket.sendall(''.join(msgs))

                client_manager.lose_repeat_clients(client)
            continue

        if tp == 'update':
            client.update_info(info.get('association_id'), info.get('domain'), info.get('team_id'))

        if GAG_MSG_SWITCH:
            continue

        if client.uid in GAG_UIDS:
            continue

        u = User.get(client.uid)
        if not settings.SESSION_SWITCH and u.ip and u.ip != client.ip:
            continue

        if settings.SESSION_SWITCH and (u.session_expired(info.get('ks'))
                                        or (u.device_mark and u.device_mark != info.get('device_mark'))
                                        or (u.device_mem and u.device_mem != info.get('device_mem'))):
            continue

        if u.is_ban:
            continue

        next_flag = info.get('next')
        if next_flag and tp in ['world', 'system', 'guild'] and next_flag in [1, 2]:
            content = content_factory.get(content_factory.MAPPINGS[tp], client.server_name)
            msgs = content.show(next_flag)
            if msgs:
                client.socket.sendall(''.join(msgs))
            continue

        con_name = content_factory.MAPPINGS.get(tp)
        if con_name and tp not in content_factory.IGNORE:
            content = content_factory.get(con_name, client.server_name)
            content.add(client.msg)

        sendToUid = info.get('sendToUid', '')
        receivers = []
        for _fd, _client in client_manager.get_client_by_server_name(client.server_name).iteritems():
            if _fd == client.fileno:
                continue
            # 判断消息是否需要发送  用gevent.spawn 处理
            if tp in ['world', 'system']:   # 世界, 系统
                receivers.append(gevent.spawn(_client.socket.sendall, _client.msg))
            elif tp == 'guild':             # 公会
                if _client.guild_id and _client.guild_id == client.guild_id:
                    receivers.append(gevent.spawn(_client.socket.sendall, client.msg))
            elif tp == 'friend' and _client.uid == sendToUid:   # 好友
                receivers.append(gevent.spawn(_client.socket.sendall, client.msg))
                break
            elif tp == 'guild_war':         # 工会战
                if _client.guild_id and client.guild_id:
                    receivers.append(gevent.spawn(_client.socket.sendall, client.msg))
            elif tp in ['rob', 'escort']:   # 运镖, 打劫
                if client.domain and client.domain == _client.domain:
                    receivers.append(gevent.spawn(_client.socket.sendall, client.msg))
            elif tp == 'team':              # 队伍
                if client.team_id and client.team_id == _client.team_id:
                    receivers.append(gevent.spawn(_client.socket.sendall, client.msg))

        # 私聊缓存
        if tp == 'friend' and sendToUid and not receivers:
            content = content_factory.get(content_factory.MAPPINGS[tp], client.server_name, sendToUid)
            content.add(client.msg)
            # content.save()

        gevent.joinall(receivers)


def close():
    content_factory.save()


def socket_server(host, port):
    print_log(__file__, '[%s] start handler_client server on port %s:%s' % (get_datetime_str(), host, port))
    server = StreamServer((host, int(port)), request_handler)
    gevent.signal(signal.SIGTERM, close)
    gevent.signal(signal.SIGINT, close)
    server.serve_forever()


if __name__ == '__main__':
    socket_server(HOST, PORT)