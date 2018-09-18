#!/usr/bin/env python
#coding: utf-8

# 创建数据库
# create database osdbadb;
# 修改数据库
# alter database testdb01 CONNECTION LIMIT 10;
# 改变数据库testdb01的名称为mydb01;
# alter database testdb01 rename to mydb01;
# 关闭数据库testdb01上的默认索引扫描
# alter database testdb01 set enable_indexscan TO off;

# 删除数据库
# drop database mytestdb01;
# drop database if exists mytestdb01;
# begin:
# alter database testdb01 rename to mydb01;
# rollback;

# 模式
# 创建、查看、删除和修改模式
# 创建一个名为"osdba"的模式
# create schema osdba;
# 查看有那些模式
# \dn

# 删除一个模式
# drop schema osdba;
# 下面的命令为用户"osdba"创建模式, 名字也定为"osdba";
# create schema authorization osdba;

# 在创建一个模式的同时, 还可以在这个模式下创建一些表的视图
# create schema osdba
#     create table t1 (id int, title text)
#     create table t2 (id int, content text)
#     create view v1 as
#         select a.id, a.title, b.content from t1 a, t2 b where a.id = b.id;

# \d 查看
# 在模式中可以修改名称和属主
# ALTER SCHEMA name RENAME TO newname
# ALTER SCHEMA name OWNER TO newowner
# 改名称的示例如下
# alter schema osdba rename to osdbaold;
# \dn 查看
# 改属主的示例如下
# alter schema osdbaold owner to web;

# 公共模式
# 要创建或者访问模式中的对象, 需要先写一个受修饰的名字, 这个名字包含模式名及表名, 它们之间用一个"点"分开
# schema_name.table_name

# 模式的搜索路径
# SHOW search_path;
# 模式的权限
# 默认的情况, 用户无法访问模式中不属于它们的对象。若要访问, 模式的所有者必须在模式上赋予它们"USAGE"权限。
# 默认在public模式上都有"CREATE"和"USAGE"权限, 允许所有连接到指定数据库上的用户在这里创建对象。可以撤销这个权限。
# REVOKE create on schema public from PUBLIC;
# 第一public是模式的名称, 第二个"PUBLIC"的意思是"所有用户"。在第一句里他是个标识符, 而第二句里是个关键字。

# 模式相当于mysql数据库

# 表
# create table test01(id int primary key, note varchar(20));
# 复合主键、约束子句的语法, 主键的约束子句语法为:
# CONSTRAINT constraint_name PRIMARY KEY (col1_name, col2_name);
# create table test02(id int, id2 int, note varchar(20), CONSTRAINT pk_test02 primary key(id1, id2));
# 唯一键约束
# CONSTRAINT constraint_name UNIQUE(col1_name, col2_name, ...);
# create table test03 (id1 int, id2 int, id3 int, note varchar(20), CONSTRAINT pk_test03 primary key(id1, id2), CONSTRAINT uk_test03_id3 UNIQUE(id3));

# check约束 检查约束
# CONSTRAINT constraint_name CHECK (expression)
# create table child(name varchar(20), age int, note text, CONSTRAINT ck_child_age CHECK(age < 18));

# 除了上面的建表方式以外, 还可以用其他表为模板创建新表
# CREATE TABLE baby (LIKE child);   # 没有把源表列上的约束复制过来
# \d baby   查看
# \d child  查看

# 如果想完全复制源表列上的约束和其他信息, 则需要加"INCLUDING"
# create table baby2 (like child including all);
# \d baby2
# 当然也可以使用create table ... as 来创建表

# 修改TOAST策略
# PLAIN: 避免压缩或线外存储
# EXTENDED: 允许压缩或线外存储
# EXTERNAL: 允许行外存储、但是不许压缩
# MAIN: 允许压缩, 但不允许行外存储。
# create table blog(id int, title text, content text);
# alter table blog alter content set storage EXTERNAL;

# 临时表(会话级别|事务级别)
# create TEMPORARY table tmp_t1 (id int primary key, note text);
# \d 本session可以看到这张表
# 其他session可以通过 \d pg_tmp_xxx.tmp_t1查看

# 事务级的临时表
# create TEMPORARY table tmp_t2 (id int primary key, note text) on commit delete rows;
# begin:
# insert into tmp_t2 values(1, 'aaa');
# insert into tmp_t2 values(2, 'bbb');
