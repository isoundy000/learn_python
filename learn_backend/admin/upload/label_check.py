#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""此模块用于对excel文件里单个标签页的内容进行数据正确性检查，主要是检查逻辑上的正确性而非格式正确性。
检测函数返回值硬性要求：
    * 函数应当有两个传入参数：sheet_title, data
    * 当检测无bug时，返回False或[]或{}或''
    * 当检测有bug时，返回非空字符串，该字符串将是展现给策划的错误提示信息,
      建议将出错的配置名加入该提示消息，同时去掉单引号'和双引号"(可调用本模块里_remove_quotes函数进行处理)

data的外观样例（server_link)：
    [
    {u'server_id': u'g2', u'country_id': 1.0, u'score': 130000.0, u'world_id': 1.0, None: u'', 'order': 1},
    {u'server_id': u'g21', u'country_id': 1.0, u'score': 130000.0, u'world_id': 1.0, None: u'', 'order': 2},
    {u'server_id': u'g30', u'country_id': 1.0, u'score': 130000.0, u'world_id': 1.0, None: None, 'order': 3},
    {u'server_id': u'g7', u'country_id': 1.0, u'score': 130000.0, u'world_id': 1.0, None: None, 'order': 4},
    {u'server_id': u'g3', u'country_id': 2.0, u'score': 130000.0, u'world_id': 1.0, None: None, 'order': 5}
    ]
"""

import settings

### 模块内工具
def _remove_quotes(string):
    string = string.replace("\"", "").replace("\'", "")
    return string


def _prefix_sheet_title(string, sheet_title):
    return str(sheet_title) + " 配置上传失败！！！原因: " + string


### 外部调用函数
def check_server_link(sheet_title, data):
    """用于对server_link列表进行检查, 有问题返回包含相关问题服务器信息的列表，无问题则返回空列表。
    server_link配置里，每个world_id里的每个country只能有一个主服（可能是主从服群）,
    如果一个特定的country里含有多个主服群里的服务器或没有任何主服，则应当报错。
    """
    error_info = []
    agent_dict = {}

    for row_data_dict in data:
        world_id = int(row_data_dict['world_id'])
        country_id = int(row_data_dict['country_id'])
        server_id = row_data_dict['server_id']
        world_country_index = str(world_id) + '_' + str(country_id)
        if world_country_index in agent_dict:
            agent_dict[world_country_index].append(server_id)
        else:
            agent_dict[world_country_index] = [server_id]

    for world_country_index, server_list in agent_dict.iteritems():
        is_OK = True
        temp_tuple_list = []
        for server in server_list:
            combined_servers = settings.get_combined(server)
            if combined_servers not in temp_tuple_list:
                temp_tuple_list.append(combined_servers)
        if len(temp_tuple_list) > 1:    # 多于一个主服群在同一个world-country服务器列表里
            is_OK = False
        if not any(map(settings.is_father_server, server_list)):    # world-country服务器列表里没有主服
            is_OK = False

        if not is_OK:
            error_info.append((world_country_index, temp_tuple_list))

    # 如果有错误，处理后返回可读性较强的返错消息
    if error_info:
        error_info = '   '.join([repr(i) for i in error_info])
        error_info = "如下world-country包含多个服务器组或缺少主服: " + error_info
        error_info = _prefix_sheet_title(error_info, sheet_title)      # 报错信息加入配置表名字
        error_info = _remove_quotes(error_info)     # 去除双引号，单引号，因有的浏览器alert显示此两字符会有问题
    return error_info