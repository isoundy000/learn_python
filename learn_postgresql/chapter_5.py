#!/usr/bin/env python
#coding: utf-8

# select 1, 1.1421, 'hello world';
# select bit '11110011';
# select int '1' + int '2';
# select cast('5' as int), cast('2018-09-15' as date);  # 类型转换函数cast
# select '5'::int, '2018-09-15'::date;                  # postgresql简洁类型转换方式, 即双冒号的方式
# create table t(id int, coll boolean, col2 text);      # 布尔类型
# select * from t where not coll;                       # 做条件
# 常用的逻辑操作服有 AND、OR、NOT
# SQL使用三值的布尔逻辑 TRUE、FALSE、NULL, NULL表示未知
# 布尔类型可以使用"IS"比较运算符
# expression IS TRUE
# expression IS NOT TRUE
# expression IS UNKNOWN
# expression IS NOT UNKNOWN

# create table t (id serial);                           # 序列类型
# 等价于声明下面几个语句
# create sequence t_id_seq;
# create table t (
#     id integer not null default nextval('t_id_seq')
# );
# alter sequence t_id_seq owned by t.id;

# 货币类型
# select '12.34'::money;
# show lc_monetary;
# set lc_monetary = 'en_US.UTF-8';

# 日期|时间类型
# create table t(coll date);
# insert into values(date, '12-10-2010');
# show datestyle;
# set datestyle = 'YMD';                                # 设置成年月日
# insert into t values(date, '2010-12-11');
# 时间输入
# select time '04:05:06';
# select time '04:05:06 PST';
# select time with time zone'04:05:06 PST';               # 时区设置
# select * from pg_timezone_abbrevs where abbrev = 'CST';
# select TIMESTAMP WITH TIME ZONE '2001-02-16 20:38:40-05' AT TIME ZONE '+08:00';

# begin;
# select CURRENT_TIME;                                # 当前时间、去掉年月日
# select CURRENT_DATE;                                # 日期
# select CURRENT_TIMESTAMP;                           # now 带时区有年月日
# select CURRENT_TIMESTAMP(2);                        # timestamptz
# select LOCALTIMESTAMP;
# end;

# begin;
# select CURRENT_TIMESTAMP;
# select now();
# select TIMESTAMP with time zone 'now';
# end;

# 枚举类型
# create type week as ENUM ('Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat');
# create TABLE duty(person text, weekday week);     # weekday 字段名, 枚举类型
# insert into duty values('张三', 'Sun');
# insert into duty values('李四', 'Mon');
# insert into duty values('王二', 'Tues');
# insert into duty values('赵五', 'Wed');

# \dT+ week                                           # 在psql中可以使用"\dT"命令查看枚举类型的定义
# select * from pg_enum;                              # 直接查询表pg_enum也可以看到枚举类型的定义
# select min(weekday), max(weekday) from duty;
# select * from duty where weekday = (select max(weekday) from duty);
# select enum_first(null::week), enum_last(null::week);

# 网络地址类型
# inet与cidr类型
# select '192.168.1.100'::inet;
# select '192.168.1.100'::cidr;
# 这两种类型输入IPv4地址的格式都为
# x.x.x.x/masklen                                      # 子网
# macaddr类型
# select '00e04c757d5a'::macaddr;
# 可以用于macaddr类型的函数只有一个: trunc(macaddr)
# select trunc(macaddr, '00e04c757d5a');

# 复合类型
# CREATE TYPE complex as (
#     r   double precision,
#     i   double precision
# );

# 定义一个"person"类型
# CREATE TYPE person as (
#     name    text,
#     age     integer,
#     sex     boolean
# );

# 定义了复合类型, 就需要次类型创建表
# create table capacitance_test_data(
#     test_time timestamp,
#     voltage    complex,             # 复合类型
#     current     complex
# );

# create table author(
#     id int,
#     person_info person,
#     book    text
# );
#
# insert into author values(1, '("张三", 29, TRUE)', '张三的自传');
# insert into author values(3, '("", , TRUE)', 'x的自传');
# insert into author values(4, ROW('张三', 29, TRUE)', '自传');
# insert into author values(5, ('张三', 29, TRUE)', '自传');
# 访问复合类型
# select (author.person_info).name from author;
# 要从一个返回复合类型值的函数中选取一个字段, 像下面的代码
# select (my_func(...).field) from ...;

# 修改复合类型
# insert into author values(('张三', 29, TRUE)', '自传');
# update author set person_info = ROW('李四', 39, TRUE) where id = 1;
# update author set person_info = ('王二', 49, TRUE) where id = 2;
# 也可以更新一个字段
# update author set person_info.name = '王二二' where id = 2;
# update author set person_info.age = (person_info).age + 1 where id = 2;
# 在insert也可以指定复合字段的子域
# insert into author (id, person_info.name, person_info.age) values(10, '张三', 29);
# 因子域没有为复合字段提供数值, 故将用NULL填充。

# xml类型, 可以倒表、库 postgresql把数据库中内容倒出成XML数据的一些函数

# json类型
# json类型的输入与输出
# select '9'::json, '"osdba"'::json, 'true'::json, 'null'::json;
# 当然也可以使用类型名放在单引号字符串前面的格式
# select json '"osdba"', json '9', json 'true', json 'null';
# 使用jsonb类型也一样
# select jsonb '"osdba"', jsonb '9', jsonb 'true', jsonb 'null';
# json中使用数组的示例如下
# select '[9, true, "osdba", null]'::json, '[9, true, "osdba", null]'::jsonb;
# json中使用字典的示例如下
# select json '{"name": "osdba", "age": 40, "sex": true, "money": 250.12}';
# 对于输入小数点的情况
# select json '{"p": 1.671111111e-27}';
# select jsonb '{"p": 1.4343434343e-27}';

# range类型
# 数组类型 输入数组值
# create table testtab05(id int, col1 int[]);
# insert into testtab05 values(1, '{1, 2, 3}');
# insert into testtab05 values(2, '{4, 5, 6}');

# box类型
# create table testtab08(id int, col1 box[]);
# insert into testtab08 values(1, '{((1,1), (2,2)); ((3,3), (4,5))}');

# create table testtab06(id int, col1 text[]);
# insert into testtab06 values(1, '{how, howe, howl}');
# insert into testtab06 values(6, ARRAY['os', 'dba']);
# insert into testtab06 values(6, ARRAY['os"dba', '123"456']);
# insert into testtab06 values(6, ARRAY['os''dab', '123''456']);

# 多维数组
# create table testtab07(id int, col1 text[][]);
# insert into testtab07 values(1, ARRAY[['os', 'dba'], ['dba', 'os']]);
# insert into testtab07 values(2, '{{a, b, null}, {c, d, e}}');

# 默认情况下, PostgreSQL数据库中数组的下标从1开始的, 但也可以指定下标的开始值
# create table test02(id, int[]);
# insert into test02 values('[2:4]={1,2,3}');
# select id[2], id[3], id[4] from test02;

# 访问数组
# select id, col1[1] from testtab5;
# select id, col1[1:2] from test02;
# create table testtab09(id int, col1 int[][]);
# insert into testtab09 values(1, '{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}');
# select id, col1[1][1], col1[1][2], col1[2][1], col1[2][2] from testtab09;
# select id, col1[1:1] from testtab09;
# select id, col1[3][1:2] from testtab09;
# select id, col1[1:2][2] from testtab09;

# 修改数组
# update testtab09 set col1 = '{{10, 11, 12}, {13, 14, 15}, {16, 17, 18}}' where id = 1;
# update testtab09 set col1[2][1] = 100 where id = 1;
# 聚合函数array_agg;

# UUID类型
# select uuid '111dasdadsasdadasdasdasdasdsaasdsdasssdasad' < uuid 'sdasddasdsadsadsadsadasdsd';