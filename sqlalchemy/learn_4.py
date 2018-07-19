# -*- encoding: utf-8 -*-
'''
Created on 2018年4月16日

@author: houguangdong
'''

# SQLAlchemy的ORM是一个映射函数（Ｍapper），将Python中定义的类与数据库中的表建立关联，以及类的实例（instance）和表的行（row）建立关联。
# 查看一个类所对应的数据库表，使用__tablename__属性，例如
# User.__tablename__

# 1.查询数据 （query）

# 1.1查询一个trace中flow个数（to count flows of specific trace）

# session.query(Flow).filter(Flow.trace_id == 1).count()

# 1.2.查询一个trace中不同srcIP的个数 （to count distinct srcIP）

from sqlalchemy import distinct

# from config import *

# session = DBSession()

# session.query(Flow.srcIP).filter(Flow.trace_id == 1).distinct().count()

# 1.3 查询一个trace中不同的dstIP和dstPort对的个数（to count distinct dstIP and dstPort）
# session.query(Flow.dstIP, Flow.dstPort).filter(Flow.trace_id == 1).distinct().count()

# 1.4查询指定列的数据，返回一个KeyedTuple数据类型的列表(get a tuple list of specified columns )

# n = session.query(Flow.dstIP, Flow.dstPort).filter(Flow.trace_id == 1).all()

# The type of n is list.

# The type of n[0] is sqlalchemy.util._collections.KeyedTuple

# 1.5 查询指定列中的所有不同值(get a distinct tuple list of specified columns)

# n = session.query(Flow.dstIP, Flow.dstPort).filter(Flow.trace_id == 1).distinct().all()

# 1.6 获得一列数据的平均值（get average value of a column）

# sql language： select avg(txPkt) from Flow
from sqlalchemy.sql import func

# q = session.query(func.avg(Flow.txPkt)).filter(Flow.trace_id == 1)

# print q[0][0]

# The type of q is sqlalchemy.orm.query.Query

# The type of q[0] is sqlalchemy.util._collections.KeyedTuple

# The type of q[0][0] is decimal.Decimal


# 1.7 多列数据平均值的计算（compute average values of columns）

# q = session.query((func.avg(Flow.txPkt) + func.avg(Flow.rxPkt)) / 2).filter(Flow.trace_id == 1)

# 1.8 对查询到的数据排序（order by ）
#
# from sqlalchemy import desc
#
# q = session.query(Flow.timestamp).filter(trace_id == 1).order_by(desc(Flow.timestamp))

# 1.9 分组查询

# q = session.query(Flow.dstIP, Flow.dstPort, func.count(Flow.id)).filter(Flow.trace_id == tid).group_by(Flow.dstIP, Flow.dstPort).all()

# 2 查询中，常用的过滤操作
# 等于(equals)， 例如 query.filter(name == 'Jack')
#
# 不等于(not equals)， 例如 query.filter(name != 'Jack')
#
# 在列表中( in)， 例如 query.filter(name.in_(['Micheal', 'Bob', 'Jack']))
#
# 不在列表中(not in)， 例如query.filter(~name.in_(['Micheal', 'Bob', 'Jack']))
#
# 空值(null), 例如 query.filter(name == None)
#
# 不是空值(not null), 例如 query.filter(name != None)
#
# 与( and), 例如 query.filter(and_(name == 'Andy', fullname == 'Andy Liu'))
# and_可以省略， 例如 query.filter(name == 'Andy', fullname ==‘Andy Liu')
#
# 或( or), 例如query.filter(or_(name == 'Andy', name == 'Micheal'))

# 2. 表的数据操作（table data operation）

# 2.1 添加\删除一个column(add a new column to a table)

from db import engine

from sqlalchemy import DDL

# add_column = DDL('alter table Flow add column cluster_id integer after trace_id')
#
# drop_column = DDL('alter table Flow drop column microsecond')
#
# engine.execute(add_column)
#
# engine.execute(drop_column)

# 2.2修改一个数据（update a value）

# session.query(Flow).filter(Flow.dstIP == dstIP, Flow.dstPort == dstPort, Flow.trace_id == 1).update({'cluster_id': 0})

# 2.3 插入一行数据（insert a row）

# session = DBSession()
#
# cluster = Clusters(trace_id=tid, cluster_id=cid, \
#  \
#                    dstIP=dIP, dstPort=dPort, \
#  \
#                    avgPkt=aPkt, avgByte=aByte, \
#  \
#                    size=count)
#
# session.add(cluster)
#
# session.commit()  # commit or flush
#
# session.close()
#
# 2.4删除一行数据（delete a row ）
#
# session = DBSession()
#
# session.query(Clusters).filter(Clusters.trace_id = 2).delete()
#
# session.commit()  # commit or flush
#
# session.close()

# 补充：
# 外键
# ForeignKey只能引用外表的指定列中已经存在的值。