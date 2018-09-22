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

# show create table t_reward_record;
# show tables like 't_god_down%';

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



# set names utf8;
# insert into t_mail2 (rid, source, type, title, content, attachment) (select r.id, 0, 'system', '时间屋属性优化补偿', '亲爱的勇者们，我们对主角的属性做了优化，对您时间屋的属性进行了重置并以强化药剂的形式返还给您。', CONCAT('{"20161":',(p.atk_a+p.def_a+p.hp_a/10),'}') from t_role r, t_protagonist p where r.id = p.id and p.atk_a+p.def_a+p.hp_a > 0);
# insert into t_mail2 (rid, source, type, title, content, attachment) (select rid, 0, 'system', '时间屋属性优化补偿', '亲爱的勇者们，我们对主角的属性做了优化，对您时间屋的属性进行了重置并以强化药剂的形式返还给您。', CONCAT('{"1001":',sum(num),'}') from t_log_usegold where opt = 'god_down_x6' and time > '2018-05-23 00:00:00' and time < '2018-05-23 02:00:00' group by rid);
# create table if not EXISTS t_favorite_general4 select * from t_favorite_general4_bak;
# create table t_favorite_general4_bak select * from t_favorite_general4;
# insert into t_mail2 (rid, source, type, title, content, attachment) (select rid, 0, 'system', 'bug修复公告', '由于线上花坊系统异常导致数据出错，现将花坊还原至今早凌晨03:00，现将今日所获取道具及在花坊内花费钻石发放，后续20：30-21:00之间将对受到影响的玩家发放补偿', CONCAT('{"20208":',sum(num),'}') from t_log_useprop where cid = 20208 and time > '2018-08-15 00:30:00' and time < '2018-08-15 20:11:00' group by rid);
# insert into t_mail2 (rid, source, type, title, content, attachment) (select rid, 0, 'system', 'bug修复公告', '由于线上花坊系统异常导致数据出错，现将花坊还原至今早凌晨03:00，现将今日所获取道具及在花坊内花费钻石发放，后续20：30-21:00之间将对受到影响的玩家发放补偿', CONCAT('{"1001":',sum(num),'}') from t_log_usegold where opt='favor2_useprop' and time > '2018-08-15 00:30:00' and time < '2018-08-15 20:11:00' group by rid);

# insert into t_mail3 (rid, source, type, title, content, attachment) (select rid, 0, 'system', 'Đền bù nhận thưởng đạo quán', 'Thưởng xếp hạng đạo quán 13.09 ', attachment from t_mail2 where title = 'Thưởng thủ vệ Đạo quán' or title = 'Chưa nhận thưởng');
# insert into t_mail3 (rid, source, type, title, content, attachment) (select rid, 0, 'system', 'Quà vũ linh đền bù 13.09', 'Thưởng xếp hạng đạo quán 13.09', CONCAT('{"',cid,'":',num-1,'}') from t_log_useprop where time > '2018-09-13 04:00:00' and time < '2018-09-13 14:10:00' and opt = 'gemdiscountshop3' and num not in (1, 10));

# select rid, cid, num, time from t_log_useprop where time > '2018-09-13 04:00:00' and time < '2018-09-13 14:10:00' and opt = 'gemdiscountshop3' and (num != 1 and num != 10);

# select rid, cid, num, time from t_log_useprop where time > '2018-09-13 04:00:00' and time < '2018-09-13 14:10:00' and opt = 'gemdiscountshop3' and num not in (1, 10);


# 18日充值大于等于388元
# select rid, sum(getgold)/10 as rmb from t_recharge_record where recvtime > '2018-09-18 00:00:00' and recvtime < '2018-09-19 00:00:00' group by rid having sum(getgold)/10 >= 388;

# 19日充值大于等于388元
# select rid, sum(getgold)/10 as rmb from t_recharge_record where recvtime > '2018-09-19 00:00:00' and recvtime < '2018-09-20 00:00:00' group by rid having sum(getgold)/10 >= 388;

# 18日充值大于100小于388
# select rid, sum(getgold)/10 as rmb from t_recharge_record where recvtime > '2018-09-18 00:00:00' and recvtime < '2018-09-19 00:00:00' group by rid having sum(getgold)/10 > 100 and sum(getgold)/ 10 < 388;

# 19日充值大于100小于388
# select rid, sum(getgold)/10 as rmb from t_recharge_record where recvtime > '2018-09-19 00:00:00' and recvtime < '2018-09-20 00:00:00' group by rid having sum(getgold)/10 > 100 and sum(getgold)/ 10 < 388;


# 获取在阵位置所有装备的cid
# select e.id, e.cid from t_equip4 as e, (select weapon, armor, accessory, head, treasure, horse from t_general4 as g, t_slot2 as s where (g.id = s.s1 or g.id = s.s2 or g.id = s.s3 or g.id = s.s4 or g.id = s.s5 or g.id = s.s6) and s.rid = 112) as b where e.id = b.weapon or e.id = b.armor or e.id = b.accessory or e.id = head or e.id = b.treasure or e.id = b.horse;

# 获取所有在阵位置的卡牌iid, cid, 装备的iid
# select g.id, g.cid, weapon, armor, accessory, head, treasure, horse from t_general4 as g, t_slot2 as s where (g.id = s.s1 or g.id = s.s2 or g.id = s.s3 or g.id = s.s4 or g.id = s.s5 or g.id = s.s6) and s.rid = 112;

