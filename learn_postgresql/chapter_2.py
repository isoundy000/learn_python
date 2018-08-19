# -*- encoding: utf-8 -*-
'''
Created on 2018年5月21日

@author: houguangdong
'''

# Debian和Ubuntu下的安装
# sudo apt-get install postgresql

# 切换用户
# su - postgres

# \l 列出所有的数据库
# apt-get安装完成的postgresql数据目录在/var/lib/postgresql/<dbversion>/main目录下

# 可以使用Liunx下的服务管理命令service来启停数据库:
# sudo service postgresql status
# sudo service postgresql start

# 在RedHat、CentOs、Fedora下的安装
# yum install postgresql-server.x86_64

# 在RedHat下安装好后，PostgreSQL服务并没有启动
# service postgresql status
# 直接启动会报错
# sudo service postgresql start
# 数据库初始化
# service postgresql initdb
# 安装第三方贡献的软件包
# yum install postgresql-contrib.x86_64
# 在RedHat或CentOs 数据目录在/var/lib/pgsql/data

# 下Ubuntu查找包的名称
# aptitude search zlib | grep dev
# 查找包含"readline"和"dev"的包
# aptitude search readline | grep dev
# 解压
# tar xvf postgresql-9.2.4.tar.bz2

# 启动和停止数据库
# pg_ctl start -D /home/osdba/pgdata
# pg_ctl stop -D /home/osdba/pgdata

# postgreSQL数据库的配置主要是通过修改数据目录下的postgresql.conf文件来实现的
# 修改监听的IP和端口
# listen_addressed = 'localhost'
# port = 5432
# 如何想让远程主机登陆 把地址改成"*"， 表示在本地的所有地址上监听
# 需要重启数据库才能生效

# 与数据库log相关的参数
# 日志的收集是要打开的
# logging_collector = on
# 日志的路径一般默认
# log_directory = 'pg_log'

# 日志的切换和是否选择覆盖如下几个方案
# 方案一： 每天生成一个新的日志文件
# log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
# log_truncate_on_rotation = off
# log_rotation_age = 1d # 每天
# log_rotation_size = 0
#
# 方案二: 每当日志写满一定的大小(如10M空间)，则切换一个日志
# log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
# log_truncate_on_rotation = off
# log_rotation_age = 0
# log_rotation_size = 10M # 大小
#
# 方案三: 只保留7天的日志，进行循环覆盖
# log_filename = 'postgresql-%a.log'
# log_truncate_on_rotation = on       # 7天循环
# log_rotation_age = 1d # 每天
# log_rotation_size = 0