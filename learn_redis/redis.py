#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/24 18:59
# @version: 0.0.1
# @Author: houguangdong
# @File: redis.py
# @Software: PyCharm

# Redis
# redis是一个key-value存储系统。和Memcached类似，它支持存储的value类型相对更多，包括string(字符串)、list(链表)、set(集合)、
# zset(sorted set --有序集合)和hash（哈希类型）。这些数据类型都支持push/pop、add/remove及取交集并集和差集及更丰富的操作，
# 而且这些操作都是原子性的。在此基础上，redis支持各种不同方式的排序。与memcached一样，为了保证效率，数据都是缓存在内存中。
# 区别的是redis会周期性的把更新的数据写入磁盘或者把修改操作写入追加的记录文件，并且在此基础上实现了master-slave(主从)同步。

# Redis安装和基本使用
# wget http://download.redis.io/releases/redis-3.0.6.tar.gz
# tar xzf redis-3.0.6.tar.gz
# cd redis-3.0.6
# make
# make install

# 启动服务端
# redis-server

# 启动客户端
# redis-cli
# set foo bar
# get foo
# "bar"

# Python操作Redis
# 安装API
# sudo pip install redis or sudo easy_install redis  源码安装 详见：https://github.com/WoLpH/redis-py

# 常用操作
# API使用
# redis-py 的API的使用可以分类为：
# 连接方式
# 连接池
# 操作
# String 操作
# Hash 操作
# List 操作
# Set 操作
# Sort Set 操作
# 管道
# 发布订阅

# 1、操作模式
# redis-py提供两个类Redis和StrictRedis用于实现Redis的命令，StrictRedis用于实现大部分官方的命令，并使用官方的语法和命令，
# Redis是StrictRedis的子类，用于向后兼容旧版本的redis-py。
import redis
r = redis.Redis(host='192.168.1.1', port=6379)
r.set('foo', 'Bar')
print(r.get('foo'))

# 2、连接池
# redis-py使用connection pool来管理对一个redis server的所有连接，避免每次建立、释放连接的开销。默认，
# 每个Redis实例都会维护一个自己的连接池。可以直接建立一个连接池，然后作为参数Redis，这样就可以实现多个Redis实例共享一个连接池。
pool = redis.ConnectionPool(host='192.168.1.1', port=6379)
r = redis.Redis(connection_pool=pool)
r.set('foo', 'Bar')
print(r.get('foo'))

# 3、操作
# 　　String操作，redis中的String在在内存中按照一个name对应一个value来存储。如图：
