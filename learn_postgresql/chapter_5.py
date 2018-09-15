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

