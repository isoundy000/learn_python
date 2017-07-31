# -*- encoding: utf-8 -*-
'''
Created on 2017年7月31日

@author: houguangdong
'''
# 使用MySQL
# 阅读: 117869
# MySQL是Web世界中使用最广泛的数据库服务器。SQLite的特点是轻量级、可嵌入，但不能承受高并发访问，适合桌面和移动应用。而MySQL是为服务器端设计的数据库，能承受高并发访问，同时占用的内存也远远大于SQLite。
# 此外，MySQL内部有多种数据库引擎，最常用的引擎是支持数据库事务的InnoDB。

# 安装MySQL
# 可以直接从MySQL官方网站下载最新的Community Server 5.6.x版本。MySQL是跨平台的，选择对应的平台下载安装文件，安装即可。
# 安装时，MySQL会提示输入root用户的口令，请务必记清楚。如果怕记不住，就把口令设置为password。
# 在Windows上，安装时请选择UTF-8编码，以便正确地处理中文。
# 在Mac或Linux上，需要编辑MySQL的配置文件，把数据库默认的编码全部改为UTF-8。MySQL的配置文件默认存放在/etc/my.cnf或者/etc/mysql/my.cnf：
# [client]
# default-character-set = utf8
# 
# [mysqld]
# default-storage-engine = INNODB
# character-set-server = utf8
# collation-server = utf8_general_ci
# 重启MySQL后，可以通过MySQL的客户端命令行检查编码：

# $ mysql -u root -p
# mysql> show variables like '%char%';
# +--------------------------+--------------------------------------------------------+
# | Variable_name            | Value                                                  |
# +--------------------------+--------------------------------------------------------+
# | character_set_client     | utf8                                                   |
# | character_set_connection | utf8                                                   |
# | character_set_database   | utf8                                                   |
# | character_set_filesystem | binary                                                 |
# | character_set_results    | utf8                                                   |
# | character_set_server     | utf8                                                   |
# | character_set_system     | utf8                                                   |
# | character_sets_dir       | /usr/local/mysql-5.1.65-osx10.6-x86_64/share/charsets/ |
# +--------------------------+--------------------------------------------------------+
# 8 rows in set (0.00 sec)
# 看到utf8字样就表示编码设置正确。

# 安装MySQL驱动
# 由于MySQL服务器以独立的进程运行，并通过网络对外服务，所以，需要支持Python的MySQL驱动来连接到MySQL服务器。
# 目前，有两个MySQL驱动：
# mysql-connector-python：是MySQL官方的纯Python驱动；
# MySQL-python：是封装了MySQL C驱动的Python驱动。
# 可以把两个都装上，使用的时候再决定用哪个：
# $ easy_install mysql-connector-python
# $ easy_install MySQL-python
# 我们以mysql-connector-python为例，演示如何连接到MySQL服务器的test数据库：

# 导入MySQL驱动:
import mysql.connector
# 注意把password设为你的root口令:
conn = mysql.connector.connect(user='root', password='donga123', database='test', use_unicode=True)
cursor = conn.cursor()
# 创建user表:
# cursor.execute('create table user (id varchar(20) primary key, name varchar(20))')
# 插入一行记录，注意MySQL的占位符是%s:
cursor.execute('insert into user (id, name) values (%s, %s)', ['2', u'侯广东'])
print cursor.rowcount
# 提交事务:
conn.commit()
cursor.close()
# 运行查询:
cursor = conn.cursor()
cursor.execute('select * from user where id = %s', ('2',))
values = cursor.fetchall()
print values
# 关闭Cursor和Connection:
cursor.close()
conn.close()

# 由于Python的DB-API定义都是通用的，所以，操作MySQL的数据库代码和SQLite类似。
# 小结
# MySQL的SQL占位符是%s；
# 通常我们在连接MySQL时传入use_unicode=True，让MySQL的DB-API始终返回Unicode。

# 最后再补充下 我还是建议手动安装参考
# http://www.cnblogs.com/Bgod/p/6995601.html mysql connector
# http://www.cnblogs.com/fnng/p/3565912.html mysql python
# create table if not exists user (id varchar(20) primary key, name varchar(20))

# MySQL-connector-python的安装
# 使用 pip 安装 出现错误 
# 到 https://dev.mysql.com/downloads/connector/python/  手动下载 
# 下载完成后：
# unzip mysql-connector-python-2.1.3.zip
# cd mysql-connector-python-2.1.3
# 进入到文件目录后安装：
# sudo python setup.py install
# 进入到安装，10秒左右完成，这样就可以在python程序里正常使用”import mysql.connector as mysql”导入MySQL的connector模块了，使用也很简单。
# 下面的代码是一个简单查询一个数据表里数据的实例：
# import mysql.connector;
# 
# try:
# conn = mysql.connector.connect(host=’172.0.0.1′, port=’3306′, user=’username’, password=”123456″, database=”testdev”, use_unicode=True);
# cursor = conn.cursor();
# cursor.execute(‘select * from t_user t where t.id = %s’, ‘1’);
# # 取回的是列表，列表中包含元组
# list = cursor.fetchall();
# print list;
#  
# for record in list:
# print “Record %d is %s!” % (record[0], record[1]);
#  
# except mysql.connector.Error as e:
# print (‘Error : {}’.format(e));
# finally:
# cursor.close;
# conn.close;
# print ‘Connection closed in finally’;