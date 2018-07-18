# -*- encoding: utf-8 -*-
'''
Created on 2018年7月13日

@author: houguangdong
'''
REDIS_CONFIG = {}

def get_redis_client_key():
    pass

def make_redis_client():
    pass

REDIS_CLIENT_DICT = {}

make_redis_client = {}

def get_redis_client_old(cls, key, server_name):
    """# get_redis_client: 获得一个redis客户端
    args:
        key, server_name:    ---    arg
    returns:
        0    ---
    """
    import hashlib
    cache_list = REDIS_CONFIG[server_name]['cache_list']
    sid = int(hashlib.md5(str(key)).hexdigest(), 16) % len(cache_list)  # redis hash分区  int(hash, 16) 表示把哈希字符串转成16进制 %len([1,2,3])表示取模
    cache_config = cache_list[sid]

    client_key = get_redis_client_key(cache_config)
    client = REDIS_CLIENT_DICT.get(client_key)

    if client is None:
        client = make_redis_client(cache_config)
        REDIS_CLIENT_DICT[client_key] = client

    return client