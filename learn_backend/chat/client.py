#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import traceback
import json
import settings

from lib.utils.debug import print_log


def get_datetime_str():
    return time.strftime('%F %T')


class Client(object):
    """
        作为一个载体，挂载一些信息
    """
    prefix = '<xml>'
    suffix = '</xml>'
    content_prefix = '<content>'
    content_suffix = '</content>'
    format_str = '<xml><length>%s</length><content>%s</content></xml>'

    CLIENT_TIMEOUT = 10 * 60    # socket最大连接时间 单位：秒
    CLOSE_CLIENT_TIMEOUT = 3 * 60  # socket最大无效连接时间 单位：秒

    def __init__(self, client_socket):
        self.socket = client_socket
        self.fileno = client_socket.fileno()
        self.ttl = int(time.time()) + self.CLIENT_TIMEOUT

        self.buffer = ''
        self.msg = ''

        self.guild_id = ''
        self.game_id = ''       # 工会战聊天模块
        self.uid = ''
        self.server_name = ''
        self.vip = 0
        self.domain = ''
        self.team_id = ''
        self.ip = ''
        self.sid = ''
        self.device_mark = ''
        self.device_mem = ''

    def init_info(self, uid, guild_id, game_id, vip, domain, team_id, ip, sid, device_mark, device_mem):
        """ 初始化数据

        :param uid: 用户uid
        :param guild_id: 联盟id
        :param game_id: 工会战聊天id
        :return:
        """
        self.uid = uid
        self.guild_id = guild_id
        self.game_id = game_id
        self.server_name = settings.get_father_server(uid[:-7])     # uid[:-7]
        self.buffer = ''
        self.domain = domain
        self.vip = int(vip)
        self.team_id = team_id
        self.ip = ip
        self.device_mem = device_mem
        self.sid = sid
        self.device_mark = device_mark

    def update_info(self, guild_id, domain, team_id):
        if guild_id is not None:
            self.guild_id = guild_id

        if domain is not None:
            self.domain = domain

        if team_id is not None:
            self.team_id = team_id

    def parse(self, data):
        """ 解析数据
        """
        self.buffer += data
        self.msg = ''

        msg = ''

        start = self.buffer.find(self.prefix)
        if start != -1:
            end = self.buffer.find(self.suffix, start)
            if end != -1:
                msg = self.buffer[start: end + len(self.suffix)]
                self.buffer = self.buffer[end + len(self.suffix):]

        if msg:
            content_start = msg.find(self.content_prefix)
            content_end = msg.find(self.content_suffix, content_start)
            if content_start == -1 or content_end == -1:
                return ''

            json_msg_str = msg[content_start + len(self.content_prefix): content_end]
            try:
                json_msg = json.loads(json_msg_str)
                json_msg['dsign'] = int(time.time())
                json_msg_str = json.dumps(json_msg)
                self.msg = self.format_str % (len(json_msg_str), json_msg_str)
                msg = json_msg
            except:
                msg = ''

        return msg



class ClientManager(object):
    """ 连接管理器

    """
    def __init__(self):
        self._clients = {}              # 所有连接
        self._server_clients = {}       # 区服对应连接

    def get_client_count(self):
        """ 获取当前连接数量
        """
        return len(self._clients)

    def get_client_by_server_name(self, server_name):
        """ 通过服务器名称获取连接

        :param server_name:
        :return:
        """
        return self._server_clients.get(server_name, {})

    def add_client(self, client):
        """ 添加一条

        :param client:
        :return:
        """
        self._clients[client.fileno] = client

    def add_server_client(self, client):
        """ 添加区服连接

        :param client:
        :return:
        """
        if client.server_name not in self._server_clients:
            self._server_clients[client.server_name] = {client.fileno: client}
        else:
            self._server_clients[client.server_name][client.fileno] = client

    def drop_client_by_fileno(self, fileno):
        """ 通过连接id删除连接的实例

        :param fileno:
        :return:
        """
        if fileno in self._clients:
            client = self._clients[fileno]
            if self._server_clients.get(client.server_name, {}).get(client.fileno):
                del self._server_clients[client.server_name][client.fileno]

            del self._clients[fileno]

    def drop_client(self, client):
        """ 通过连接, 删除连接的实例

        :param client:
        :return:
        """
        if self._server_clients.get(client.server_name, {}).get(client.fileno):
            del self._server_clients[client.server_name][client.fileno]

        if client.fileno in self._clients:
            del self._clients[client.fileno]

    def lose_client_by_fileno(self, fileno):
        """ 通过连接id断开连接实例

        :param fileno:
        :return:
        """
        client = self._clients.get(fileno)
        if client:
            self.drop_client_by_fileno(fileno)
            client.disconnect()
            del client

    def lose_client(self, client):
        """ 通过连接, 断开连接实例

        :param client:
        :return:
        """
        _client = self._clients.get(client.fileno)

        if _client:
            self.drop_client(_client)

            _client.disconnect()

            del _client
        else:
            del client

    def lose_time_out_clients(self, now=None):
        """ 关闭超时的连接实例  10 - 3 < 10 - 3

        """
        now = now or int(time.time())

        timeout_sockets = []

        for _fd, _client in self._clients.iteritems():
            if now > _client.ttl or (not _client.uid and _client.ttl - now < _client.CLIENT_TIMEOUT - _client.CLOSE_CLIENT_TIMEOUT):
                timeout_sockets.append(_client)

        for _client in timeout_sockets:
            self.lose_client(_client)

    def lose_repeat_clients(self, client):
        """ 关闭重复的连接实例

        """
        clients = self.get_client_by_server_name(client.server_name)

        repeat_sockets = []

        for _fd, _client in clients.iteritems():
            if _client.uid and _client.uid == client.uid and _fd != client.fileno:
                repeat_sockets.append(_client)

        for _client in repeat_sockets:
            self.lose_client(_client)