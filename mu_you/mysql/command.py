# -*- encoding: utf-8 -*-
'''
Created on 2018年8月21日

@author: houguangdong
'''

# mysql -usanguo_bg -psanguo_passwd --socket=/data/mysql1/mysql.sock -e "use hot_yuenan_game_1; show tables;" > /home/ghou/tables.txt

# sql文件
# source /home/ghou/tmp.sql;

# 119.29.82.181 管理机日志
# /data/hotblood_log/62

# 热血越南香港跳板机
# IP: 47.89.22.125
# user: t_hotboy
# pass: r<2q"S;h
# port ssh: 22

# 从跳版机下载代码
# tar zcf source.tar.gz source/
# scp source.tar.gz 47.89.22.125:/home/t_hotboy


# diff -r source999999/ source|grep -v pyo


# 创建备份表
# create table if not EXISTS t_god_down_hou select * from t_god_down2018_09_12;
# create table if not EXISTS t_god_down_dong select * from t_god_down;

# 备份表和新表的数据叠加
# update t_god_down_dong a, t_god_down_hou b set a.total_point = a.total_point + b.total_point, a.point = a.point + b.point where a.rid = b.rid;

# 另外一种方法是使用inner join然后更新：
# update t_god_down_dong p inner join t_god_down_hou pp on p.rid = pp.rid set p.total_point = p.total_point + pp.total_point, p.point = p.point + pp.point where pp.total_point > 0;

# 我们也可以使用left outer join来做多表update，比方说如果ProductPrice表中没有产品价格记录的话，将Product表的isDeleted字段置为1，如下sql语句：
# update t_god_down_dong p left join t_god_down_hou pp on p.rid = pp.rid set p.c2 = 1 where pp.c2 = 1;

# 上面的几个例子都是两张表之间做关联，但是只更新一张表中的记录，其实是可以同时更新两张表的，如下sql：
# UPDATE product p INNER JOIN productPrice pp ON p.productId = pp.productId SET pp.price = pp.price * 0.8,
# p.dateUpdate = CURDATE()
# WHERE p.dateCreated < '2004-01-01';

# update t_god_down_dong p inner join t_god_down_hou pp on p.rid = pp.rid set p.c5 = 6, pp.c1 = 0 where pp.c5 = 6;

# 两张表做关联，更新了ProductPrice表的price字段和Product表字段的dateUpdate两个字段。