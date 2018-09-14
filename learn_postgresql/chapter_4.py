#!/usr/bin/env python
#coding: utf-8

# psql的命令都是以"\"开头的
# 查看数据库
# psql -l = \l

# 创建数据库
# create database testdb;
# 使用 \c testdb就可连接到testdb上
# 常用的psql连接数据库的方法, 命令格式如下
# psql -h <hostname or ip> -p <端口> [数据库名称] [用户名称]
# psql -h 192.168.56.11 -p 5432 testdb postgres
# 连接参数用环境变量指定
# export PGDATABASE=testdb
# export PGHOST=192.168.56.11
# export PGPORT=5432
# export PGUSER=postgres
# \d命令
# \d命令什么都不带, 列出当前数据库中所有表
# \d student 显示表的结构定义
# \d t_pkey 显示索引的信息
# \d 后面也可以跟一通配符如"*"或"?"
# \d x?
# \d t*
# \d+ t t表更详细的信息
# 匹配不同对象类型的\d命令
# 1 如果想只显示匹配的表 可以使用\dt命令
# 2 如果想只显示索引 可以使用\di命令
# 3 如果想只显示序列 可以使用\ds命令
# 4 如果想只显示视图 可以使用\dv命令
# 5 如果想只显示函数 可以使用\df命令
# 如果想显示SQL已执行的时间, 可以用\timing命令
# \timing on
# 列出所有的schema可以使用\dn命令
# 显示所有的表空间可以使用\db命令
# 列出数据库中所有的角色或用户 可以使用\du或\dg命令
# \dp或\z命令用于显示表的权限分配情况 \dp t
# \encoding utf8|gbk; 命令设置客户端的字符编码为gbk;

# \pset命令
# \pset命令用于设置输出的格式
# \pset border 0: 表示输出内容无边框
# \pset border 1: 表示边框只在内部
# \pset border 2: 表示内外都有边框
# eg:
# \pset border 0;
# select * from x1;

# \x命令, 可以把表每一行的每列数据都拆分为单行展示
# select * from pg_stat_activity;

# 执行存储在外部文件中的SQL命令
# 命令\i<文件名>执行存储在外部文件中的sql语句或命令
# \i getrunsql
# 可以在psql命令行加-s <filename>来执行SQL脚本文件中的命令
# psql -x -f getrunsql
# 其中命令行参数"-x"相当于在psql交互模式下运行"\x"命令

# 显示信息的命令
# \echo hello world
# eg:
# \echo =======================
# select * from x1;
# \echo =======================
# 运行a.sql脚本
# \i a.sql

# 更多的命令可以用\?来显示
# 历史命令与补全的功能
# \d <--这里连续按两个tab键
# \d t <--这里连续按两个tab键
# \d x <--这里连续按两个tab键
# \d x

# 不自动提交事务的方法
# 方式1
# begin;
# update x1 set name = 'xxxx' where id = 1;
# select * form x1;
# rollback;
# select * from x1;
# 方式2 直接使用psql中的命令关闭自动提交的功能 AUTOCOMMIT必须大写
# \set AUTOCOMMIT off

# 如何得到psql中命令实际执行的SQL
# 如果在启动psql的命令行中加"-E"参数，就可以把psql中各种以"\"开头的命令执行的实际SQL打印出来
# eg:
# psql -E postgres
# \d
# \d testtable*
# 如果想在已运行的psql中显示某一个命令实际执行的SQL，但显示完后又想关闭这个功能。可以使员工\set ECHO_HIDDEN on|off
# eg:
# psql postgres
# \dn
# \set ECHO_HIDDEN on
# \dn
# \set ECHO_HIDDEN off