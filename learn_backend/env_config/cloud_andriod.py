#!/usr/bin/env python
# -*- coding:utf-8 -*-

host_list = [
    # server server_host web_local_port redis_ip redis_port redis_db env config_type
    ('g1', 'localhost', (2500, 2507), 'localhost', 6379, 15, 'cloud_android', 1),

    ('g2', 'localhost', (2100, 2107), 'localhost', 6379, 14, 'cloud_android', 3, 'g3'),
    ('g3', 'localhost', (2200, 2207), 'localhost', 6379, 13, 'cloud_android', 2),
    ('g4', 'localhost', (2300, 2307), 'localhost', 6379, 12, 'cloud_android', 4),
    ('g5', 'localhost', (2400, 2407), 'localhost', 6379, 11, 'cloud_android', 1),
]


def cloud_andriod(service_name):

    arguments = {}

    arguments['PLATFORM'] = 'pub'
    arguments['URL_PARTITION'] = URL_PARTITION = 'genesisandroidios'

    # URL_PARTITION_1 = 'genesisandroidios_1'
    # URL_PARTITION_2 = 'genesisandroidios_2'
    # URL_PARTITION_3 = 'genesisandroidios_3'

    MASTER_CACHE = [
        {'host': '127.0.0.1', 'port': 6379, 'socket_timeout': 5, 'db': 0, 'password': 'F8974044A778'}
    ]

    MASTER_HOST = '127.0.0.1'
    CHAT_IDS = ['127.0.0.1', '127.0.0.1']

    arguments['DEBUG'] = False

    arguments['SERVER_LIST_URL'] = 'http://%s/%s/config/?method=server_list' % (MASTER_HOST, URL_PARTITION)

    arguments.update({
        # LUA_RESOURCE_GIT_PATH: '/data/mashajie/s/genesis/genesis_pub_kuaiyong_tongbutui_client_repo/',
        'PAYLOG_HOST': {
            'host': '127.0.0.1',
            'user': 'root',
            'passwd': '390dc437551c62',
            'db': 'genesis',
            'table_prefix': 'paylog'
        },
        'SPENDLOG_HOST': {
            # 'host': '10.10.15.190',
            'host': '127.0.0.1',
            'user': 'root',
            'passwd': '390dc437551c62',
            'db': 'genesis',
            'table_prefix': 'spendlog'
        },
        'PAYMENT_CACHE': {
            'host': '127.0.0.1',
            'port': 6379,
            'socket_timeout': 5,
            'db': 3,
            'password': 'F8974044A778',
        },
        'ACTIVATION_CODE': {
            'host': '127.0.0.1',
            'port': 6379,
            'socket_timeout': 5,
            'db': 2,
            'password': 'F8974044A778',
        },
        'AD_CLICK': {
            'host': '127.0.0.1',
            'port': 6379,
            'socket_timeout': 5,
            'db': 4,
            'password': 'F8974044A778',
        },
        'TEAM_PK': {
            'host': '127.0.0.1',
            'port': 6379,
            'socket_timeout': 5,
            'db': 0,
            'password': 'F8974044A778',
        },
        'LARGE': {
            'host': '127.0.0.1',
            'port': 6379,
            'socket_timeout': 5,
            'db': 0,
            'password': 'F8974044A778',
        },
        'SERVERS': {
            'master': {                 # 现在他的server已经没有意义，更像是个标示效果
                'server': 'http://%s/%s/' % (MASTER_HOST, URL_PARTITION),
                'cache_list': MASTER_CACHE,
            },
        },
    })

    chat_ips_len = len(CHAT_IDS)

    x = []
    for k, i in enumerate(host_list):
        if i[0] in x:
            continue
        father_server = i[8] if len(i) > 8 and i[8] else i[0]
        arguments['SERVERS'][i[0]] = {

        }