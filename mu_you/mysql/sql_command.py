#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'
#
# 用户渠道对比
# select uid,channel_id from users_0
#
# 新增(不用)
# select uid from users_0 where  from_unixtime(add_time)  between '2020-03-10 00:00:00' and '2020-03-10 23:59:59';
# select uid from users_0 where  from_unixtime(add_time)  between '2020-03-11 00:00:00' and '2020-03-11 23:59:59';
#
# dau
# select channel_id,count(distinct uid) from users_0 where from_unixtime(login_time) between '2020-03-11 00:00:00' and '2020-03-11 23:59:59' group by channel_id;
#
#
# 付费金额，人数,次数
# select uid,sum(amount),count(*) from subrecord where is_real=1 and from_unixtime(add_time) between '2020-03-11 00:00:00' and '2020-03-11 12:00:00' group by uid;
#
# 新用户付费 # 账号创建时间也当日
# select uid,sum(amount) from subrecord where is_real=1 and from_unixtime(add_time) BETWEEN '2020-03-11 00:00:00'  AND '2020-03-11 20:00:00'  AND uid in () group by uid;
#
# 9日新登次留
# select channel_id,count(distinct uid) from users_0 where from_unixtime(login_time)='2020-03-10' and uid in () group by channel_id;
#
#
# ltv
# select uid,sum(amount),count(*) from subrecord where is_real=1 and  from_unixtime(add_time) between '2020-03-09 00:00:00' and '2020-03-12 10:00:00' and uid in () group by uid;
#
# 新增
# select channel_id,count(uid) from users_0 where FROM_UNIXTIME(add_time) BETWEEN '2020-03-12 00:00:00' AND '2020-03-12 10:00:00' group by channel_id;
#
# 5服 次流
# select channel_id,count(distinct uid) from users_0 where from_unixtime(login_time) between '2020-03-10 00:00:00' and '2020-03-10 23:59:59' and from_unixtime(add_time) between '2020-03-10 00:00:00' and '2020-03-10 23:59:59' group by channel_id;
# 1 -4 服 次流
# select channel_id,count(distinct uid) from users_0 where from_unixtime(login_time) between '2020-03-11 00:00:00' and '2020-03-11 23:59:59' and from_unixtime(add_time) between '2020-03-10 00:00:00' and '2020-03-10 23:59:59' group by channel_id;
# 1 -4 服 3流
# select channel_id,count(distinct uid) from users_0 where from_unixtime(login_time) between '2020-03-11 00:00:00' and '2020-03-11 23:59:59' and from_unixtime(add_time) between '2020-03-09 00:00:00' and '2020-03-09 23:59:59' group by channel_id;
#
# 设备激活
# select channel_id, uid, openid from users_0 where FROM_UNIXTIME(add_time) BETWEEN '2020-03-12 00:00:00' AND '2020-03-12 10:00:00';