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