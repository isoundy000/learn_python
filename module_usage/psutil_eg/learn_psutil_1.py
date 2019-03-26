# -*- coding: utf-8-*-

# python计算非内置数据类型占用内存

# 阅读目录
# getsizeof的局限
# 使用psutil模块获取内存
# python模块psutil简介
# psutil获取系统状态举例
# getsizeof的局限
# python非内置数据类型的对象无法用sys.getsizeof()获得真实的大小，例：
# import networkx as nx
# import sys
# G = nx.Graph()
# l = [i for i in xrange(10000)]
# print "size of l:", sys.getsizeof(l)
# G.add_nodes_from(l)
# print "size of graph:", sys.getsizeof(G)
# 结果
# size of l: 87632
# size of graph: 64
# 分析
# 图graph中包含点序列l,而大小还不如l的大小，所以用getsizeof计算python的非内置类型的对象大小时是不准的。
#
# 使用psutil模块获取内存
#
# 例1：
#
# 复制代码
# import networkx as nx
# import psutil
# import sys
# import os
# G = nx.Graph()
# l = [i for i in xrange(10000)]
# print "size of l:", sys.getsizeof(l)
# G.add_nodes_from(l)
# print "size of graph:", sys.getsizeof(G)
# process = psutil.Process(os.getpid())
# max_mem = process.memory_info().rss
# print 'max_mem:', max_mem
# 复制代码
# 这样得到的有问题，需要把一开始系统所占的内存去掉
#
# 复制代码
# import psutil
# import sys
# import os
#
# process = psutil.Process(os.getpid())
#
# max_mem_1 = process.memory_info().rss
# print 'max_mem:', max_mem_1
#
# G = nx.Graph()
# l = [i for i in xrange(10000)]
# G.add_nodes_from(l)
#
# max_mem_2 = process.memory_info().rss
# print 'max_2:', max_mem_2
# print 'max_mem:', max_mem_2 - max_mem_1
# 复制代码
# 结果
#
# max_mem: 23724032
# max_2: 31637504
# max_mem: 7913472
# 例2：
#
# 复制代码
# import psutil
# import os
# import sys
# from datetime import datetime
#
# process = psutil.Process(os.getpid())
#
# max_mem_1 = process.memory_info().rss / 1024.0 / 1024.0 / 1024.0
# print 'max_mem 1:', max_mem_1
#
# all_road_nx = 'a' * 1024 * 1024 * 1024 * 10;
# print 'size:', sys.getsizeof(all_road_nx)/ 1024.0 / 1024.0 / 1024.0
# print 'len all_road_nx:', len(all_road_nx)
#
#
# max_mem_2 = process.memory_info().rss / 1024.0 / 1024.0 / 1024.0
# print 'max_mem 2:', max_mem_2
#
# print 'max_mem 3:', max_mem_2 - max_mem_1
# 复制代码
# 结果：
#
# max_mem 1: 0.00862503051758
# size: 10.0000000345
# len all_road_nx: 10737418240
# max_mem 2: 10.0086517334
# max_mem 3: 10.0000267029
# 回到顶部
# python模块psutil简介
#
# psutil提供了个接口，可以用来获取信息，包括：
#
# 当前运行的进程
# 系统（资源使用）信息
# CPU
# 内存
# 磁盘
# 网络
# 用户
# psutil实现了很多功能，包括了如下工具所具有的：
#
# ps
# top
# df
# kill
# free
# lsof
# free
# netstat
# ifconfig
# nice
# ionice
# iostat
# iotop
# uptime
# pidof
# tty
# who
# taskset
# pmap
# 回到顶部
# psutil获取系统状态举例
#
# 复制代码
# #! coding:utf-8
# import networkx as nx
# import psutil
# import sys
# import os
#
# p = psutil.Process(os.getpid())
#
# psutil.pids()  #查看系统全部进程
# p = psutil.Process(6241)  #查看系统全部进程
# print "name:", p.name()   #进程名
# print "bin 路径", p.exe()    #进程的bin路径
# print "进程绝对路径", p.cwd()    #进程的工作目录绝对路径
# print "进程状态", p.status()   #进程状态
# print "进程创建时间", p.create_time()  #进程创建时间
# print "进程uuid信息", p.uids()    #进程uid信息
# print "进程gid信息", p.gids()    #进程的gid信息
# print "进程的cpu时间信息", p.cpu_times()   #进程的cpu时间信息,包括user,system两个cpu信息
# print "get进程cpu亲和度", p.cpu_affinity()  #get进程cpu亲和度,如果要设置cpu亲和度,将cpu号作为参考就好
# print "进程内存利用率", p.memory_percent()  #进程内存利用率
# print "进程内存rss,vms信息", p.memory_info()    #进程内存rss,vms信息
# print "进程的IO信息", p.io_counters()    #进程的IO信息,包括读写IO数字及参数
# print "进程列表", p.connections()   #返回进程列表
# print "进程开启的线程数", p.num_threads()  #进程开启的线程数
# 复制代码
# 结果
#
# 复制代码
# name: python
# bin 路径 /home/tops/bin/python2.7
# 进程绝对路径 /home/jihite/iu_iso_test
# 进程状态 sleeping
# 进程创建时间 1463322002.74
# 进程uuid信息 puids(real=124674, effective=124674, saved=124674)
# 进程gid信息 pgids(real=100, effective=100, saved=100)
# 进程的cpu时间信息 pcputimes(user=14.38, system=2.38, children_user=0.0, children_system=0.0)
# get进程cpu亲和度 [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
# 进程内存利用率 0.0432284208934
# 进程内存rss,vms信息 pmem(rss=58548224, vms=534482944, shared=6922240, text=1536000, lib=0, data=268894208, dirty=0)
# 进程的IO信息 pio(read_count=4166, write_count=1192, read_bytes=0, write_bytes=0)
# 进程列表 [pconn(fd=3, family=2, type=1, laddr=('10.184.70.11', 57785), raddr=('10.184.70.13', 8018), status='ESTABLISHED')]
# 进程开启的线程数 4