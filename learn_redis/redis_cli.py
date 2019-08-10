# -*- encoding: utf-8 -*-
'''
Created on 2019年7月13日

@author: houguangdong
'''

import redis
pool = redis.BlockingConnectionPool(retry_on_timeout=True,
    **{'host': "127.0.0.1", 'port': 6379, 'socket_timeout': 5, 'db': 0, 'password': 'donga123'})

redis_conn = redis.Redis(connection_pool=pool)

pool1 = redis.BlockingConnectionPool(retry_on_timeout=True,
    **{'host': "127.0.0.1", 'port': 6379, 'socket_timeout': 5, 'db': 1, 'password': 'donga123'})

redis_conn1 = redis.Redis(connection_pool=pool1)

# print redis_conn, redis_conn1

redis_conn.set('k1', 'v1')      # 向远程redis中写入了一个键值对
val = redis_conn.get('k1')      # 获取键值对
print(val)

redis_conn1.set('k3', 'v3')     # 向远程redis中写入了一个键值对
val1 = redis_conn1.get('k2')    # 获取键值对
print val1

def read_type_keys(source, keys=None):
    keys = keys or source.keys()
    keys_count = len(keys)
    print "Key Count is:", keys_count
    pipe = source.pipeline(transaction=False)
    result = {'string_keys': [], 'list_keys': [], 'hash_keys': [], 'set_keys': [], 'zset_keys': []}
    index = 0
    pipe_size = 5000
    while index < keys_count:
        old_index = index
        num = 0
        while (index < keys_count) and (num < pipe_size):
            pipe.type(keys[index])
            index += 1
            num += 1
        results = pipe.execute()
        for tp in results:
            value = keys[old_index]
            if tp == "string":
                result['string_keys'].append(value)
            elif tp == "list":
                result['list_keys'].append(value)
            elif tp == "hash":
                result['hash_keys'].append(value)
            elif tp == "set":
                result['set_keys'].append(value)
            elif tp == "zset":
                result['zset_keys'].append(value)
            else:
                print value, " is not find when TYPE"
            old_index += 1
    return result


if __name__ == "__main__":
    print read_type_keys(redis_conn1)