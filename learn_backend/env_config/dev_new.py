#!/usr/bin/python
# encoding: utf-8

# redis分配：0~9 - dev, 10~19 - test
def dev_new(service_name):
    arguments = {}
    arguments['URL_PARTITION'] = URL_PARTITION = 'genesis'
    MASTER_CACHE = [
        {'host': '127.0.0.1', 'port': 6379, 'socket_timeout': 5, 'max_connections': 5, 'db': 0}    #  'password': 'a66c8e6faad505b2'
    ]
    CACHES = [
        {'host': '127.0.0.1', 'port': 6379, 'socket_timeout': 5, 'max_connections': 5, 'db': 1},    #, 'password': 'a66c8e6faad505b2'
    ]
    CACHES_h2 = [
        {'host': '127.0.0.1', 'port': 6379, 'socket_timeout': 5, 'max_connections': 5, 'db': 2},    #, 'password': 'a66c8e6faad505b2'
    ]
    CACHES_h3 = [
        {'host': '127.0.0.1', 'port': 6379, 'socket_timeout': 5, 'max_connections': 5, 'db': 3},    # , 'password': 'a66c8e6faad505b2'
    ]
    CACHES_h4 = [
        {'host': '127.0.0.1', 'port': 6379, 'socket_timeout': 5, 'max_connections': 5, 'db': 4},    # , 'password': 'a66c8e6faad505b2'
    ]
    CACHES_h5 = [
        {'host': '127.0.0.1', 'port': 6379, 'socket_timeout': 5, 'max_connections': 5, 'db': 5},    #, 'password': 'a66c8e6faad505b2'
    ]
    h1_config = {
        'server': 'http://localhost/%s/' % URL_PARTITION,
        'dataosha': 'http://localhost/%s/dataosha' % URL_PARTITION,
        'lua': 'http://localhost/%s/lr/' % URL_PARTITION,
        'lua_ver_url': 'http://localhost/%s/' % URL_PARTITION,
        'chat_ip': 'localhost',
        'chat_port': 9005,
        'cache_list': CACHES,
        'father_server': '',
        'combined_servers': [],
        'config_type': 1,
    }
    h2_config = {
        'server': 'http://localhost/%s/' % URL_PARTITION,
        'dataosha': 'http://localhost/%s/dataosha' % URL_PARTITION,
        'lua': 'http://localhost/%s/lr/' % URL_PARTITION,
        'lua_ver_url': 'http://localhost/%s/' % URL_PARTITION,
        'chat_ip': 'localhost',
        'chat_port': 9005,
        'cache_list': CACHES_h2,
        'father_server': '',
        'combined_servers': [],
        'config_type': 1,
        'URL_PARTITION': URL_PARTITION,
    }
    h3_config = {
        'server': 'http://localhost/%s/' % URL_PARTITION,
        'dataosha': 'http://localhost/%s/dataosha' % URL_PARTITION,
        'lua': 'http://localhost/%s/lr/' % URL_PARTITION,
        'lua_ver_url': 'http://localhost/%s/' % URL_PARTITION,
        'chat_ip': 'localhost',
        'chat_port': 9005,
        'cache_list': CACHES_h3,
        'father_server': '',
        'combined_servers': [],
        'config_type': 1,
        'URL_PARTITION': URL_PARTITION,
    }
    h4_config = {
        'server': 'http://localhost/%s/' % URL_PARTITION,
        'dataosha': 'http://localhost/%s/dataosha' % URL_PARTITION,
        'lua': 'http://localhost/%s/lr/' % URL_PARTITION,
        'lua_ver_url': 'http://localhost/%s/' % URL_PARTITION,
        'chat_ip': 'localhost',
        'chat_port': 9005,
        'cache_list': CACHES_h4,
        'father_server': '',
        'combined_servers': [],
        'config_type': 1,
        'URL_PARTITION': URL_PARTITION,
    }
    h5_config = {
        'server': 'http://localhost/%s/' % URL_PARTITION,
        'dataosha': 'http://localhost/%s/dataosha' % URL_PARTITION,
        'lua': 'http://localhost/%s/lr/' % URL_PARTITION,
        'lua_ver_url': 'http://localhost/%s/' % URL_PARTITION,
        'chat_ip': 'localhost',
        'chat_port': 9005,
        'cache_list': CACHES_h5,
        'father_server': '',
        'combined_servers': [],
        'config_type': 1,
        'URL_PARTITION': URL_PARTITION,
    }
    arguments.update({
        'PAYMENT_CACHE': {
            'host': '127.0.0.1',
            'port': 6379, 'socket_timeout': 5, 'max_connections': 5,
            'db': 0,
            # 'password': 'a66c8e6faad505b2',
        },
        'PAYLOG_HOST': {
            'host': '127.0.0.1',
            'user': 'root',
            'passwd': '123456',                 # '60fc859bfaebc064',
            'db': 'genesis',
            'table_prefix': 'paylog'
        },
        'SPENDLOG_HOST': {
            'host': '127.0.0.1',
            'user': 'root',
            'passwd': '60fc859bfaebc064',
            'db': 'genesis',
            'table_prefix': 'spendlog'
        },
        'ACTIVATION_CODE': {
            'host': '127.0.0.1',
            'port': 6379, 'socket_timeout': 5, 'max_connections': 5,
            'db': 0,
            # 'password': 'a66c8e6faad505b2',
        },
        'AD_CLICK': {
            'host': '127.0.0.1',
            'port': 6379, 'socket_timeout': 5,
            'db': 0,
            # 'password': 'a66c8e6faad505b2',
        },
        'TEAM_PK': {
            'host': '127.0.0.1',
            'port': 6379, 'socket_timeout': 5,
            'db': 0,
            # 'password': 'a66c8e6faad505b2',
        },
        'LARGE': {
            'host': '127.0.0.1',
            'port': 6379, 'socket_timeout': 5,
            'db': 0,
            # 'password': 'a66c8e6faad505b2',
        },
        'SERVERS': {
            'master': {
                'server': 'http://localhost/%s/' % URL_PARTITION,
                'dataosha': 'http://localhost/%s/dataosha' % URL_PARTITION,
                'lua': 'http://localhost/%s/lr/' % URL_PARTITION,
                'iphonehd': 'http://localhost/%s/lr/' % URL_PARTITION,
                'cache_list': MASTER_CACHE,
                'config_type': 1,
            },
            'h1': h1_config,
            'h2': h2_config,
            'h3': h3_config,
            'h4': h4_config,
            'h5': h5_config,
        },
    })
    arguments['SERVICE_NAME'] = service_name

    # vivo平台充值回调地址
    arguments['VIVO_PAY_CALLBACK_URL'] = 'http://localhost/%s/pay/?method=callback&tp=vivo' % URL_PARTITION
    # 金立手机平台充值回调地址
    arguments['JINLI_PAY_CALLBACK_URL'] = 'http://localhost/%s/pay/?method=callback&tp=jinli' % URL_PARTITION
    arguments['PAYMENT_NOTIFY_URLS'] = {}
    for pt in ['360', 'lenovo', 'coolpad', 'oppo', 'youku', 'lenovo2', 'lenovo3', 'xmw', 'xmw2', 'wanpu', 'yy', 'lewan', 'yaowang']:
        arguments['PAYMENT_NOTIFY_URLS'][pt] = 'http://localhost/%s/pay-callback-%s/' % (URL_PARTITION, pt)
    return arguments