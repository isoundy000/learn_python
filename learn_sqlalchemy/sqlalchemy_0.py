#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/24 22:46
# @version: 0.0.1
# @Author: houguangdong
# @File: sqlalchemy.py
# @Software: PyCharm

# SQLAlchemy
# SQLAlchemy是Python编程语言下的一款ORM框架，该框架建立在数据库API之上，使用关系对象映射进行数据库操作，
# 简言之便是：将对象转换成SQL，然后使用数据API执行SQL并获取执行结果。


# Dialect用于和数据API进行交流，根据配置文件的不同调用不同的数据库API，从而实现对数据库的操作，如：
# MySQL-Python
#     mysql+mysqldb://<user>:<password>@<host>[:<port>]/<dbname>
# pymysql
#     mysql+pymysql://<username>:<password>@<host>/<dbname>[?<options>]
# MySQL-Connector
#     mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
# cx_Oracle
#     oracle+cx_oracle://user:pass@host:port/dbname[?key=value&key=value...]

# 步骤一：
# 使用 Engine/ConnectionPooling/Dialect进行数据库操作，Engine使用ConnectionPooling连接数据库，
# 然后再通过Dialect执行SQL语句。
from sqlalchemy import create_engine
engine = create_engine("mysql+mysqldb://root:123@127.0.0.1:3306/s11", max_overflow=5)

engine.execute(
    "INSERT INTO ts_test (a, b) VALUES ('2', 'v1')"
)
engine.execute(
    "INSERT INTO ts_test (a, b) VALUES (%s, %s)",
    ((555, "v1"), (666, "v1"),)
)
engine.execute(
    "INSERT INTO ts_test (a, b) VALUES (%(id)s, %(name)s)",
    id=999, name="v1"
)
result = engine.execute('select * from ts_test')
result.fetchall()


# ########################## 事务操作 ##########################
engine = create_engine("mysql+mysqldb://root:123@127.0.0.1:3306/s11", max_overflow=5)

# 事务操作
with engine.begin() as conn:
    conn.execute("insert into table (x, y, z) values (1, 2, 3)")
    conn.execute("my_special_procedure(5)")

conn = engine.connect()
# 事务操作
with conn.begin():
    conn.execute("some statement", {'x': 5, 'y': 10})

# 查看数据库连接：show status like 'Threads%';
# 步骤二：
# 使用 Schema Type/SQL Expression Language/Engine/ConnectionPooling/Dialect 进行数据库操作。
# Engine使用Schema Type创建一个特定的结构对象，之后通过SQL Expression Language将该对象转换成SQL语句，
# 然后通过 ConnectionPooling 连接数据库，再然后通过 Dialect 执行SQL，并获取结果。
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey

metadata = MetaData()

user = Table('user', metadata,
             Column('id', Integer, primary_key=True),
             Column('name', String(20)),
             )

color = Table('color', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(20)),
              )
engine = create_engine("mysql+mysqldb://root:123@127.0.0.1:3306/s11", max_overflow=5)

metadata.create_all(engine)
# metadata.clear()
# metadata.remove()



# ########################## 增删改查 ##########################
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey

metadata = MetaData()

user = Table('user', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(20)),
)

color = Table('color', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(20)),
)
engine = create_engine("mysql+mysqldb://root:123@127.0.0.1:3306/s11", max_overflow=5)

conn = engine.connect()

# 创建SQL语句，INSERT INTO "user" (id, name) VALUES (:id, :name)
conn.execute(user.insert(),{'id':7,'name':'seven'})
conn.close()

# sql = user.insert().values(id=123, name='wu')
# conn.execute(sql)
# conn.close()

# sql = user.delete().where(user.c.id > 1)

# sql = user.update().values(fullname=user.c.name)
# sql = user.update().where(user.c.name == 'jack').values(name='ed')

# sql = select([user, ])
# sql = select([user.c.id, ])
# sql = select([user.c.name, color.c.name]).where(user.c.id==color.c.id)
# sql = select([user.c.name]).order_by(user.c.name)
# sql = select([user]).group_by(user.c.name)

# result = conn.execute(sql)
# print result.fetchall()
# conn.close()
# SQLAlchemy无法修改表结构，如果需要可以使用SQLAlchemy开发者开源的另外一个软件Alembic来完成。


# 步骤三：
# 使用 ORM/Schema Type/SQL Expression Language/Engine/ConnectionPooling/Dialect 所有组件对数据进行操作。
# 根据类创建对象，对象转换成SQL，执行SQL。
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine("mysql+mysqldb://root:123@127.0.0.1:3306/s11", max_overflow=5)

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))


# 寻找Base的所有子类，按照子类的结构在数据库中生成对应的数据表信息
# Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


# ########## 增 ##########
# u = User(id=2, name='sb')
# session.add(u)
# session.add_all([
#     User(id=3, name='sb'),
#     User(id=4, name='sb')
# ])
# session.commit()

# ########## 删除 ##########
# session.query(User).filter(User.id > 2).delete()
# session.commit()

# ########## 修改 ##########
# session.query(User).filter(User.id > 2).update({'cluster_id' : 0})
# session.commit()
# ########## 查 ##########
# ret = session.query(User).filter_by(name='sb').first()

# ret = session.query(User).filter_by(name='sb').all()
# print ret

# ret = session.query(User).filter(User.name.in_(['sb','bb'])).all()
# print ret

# ret = session.query(User.name.label('name_label')).all()
# print ret,type(ret)

# ret = session.query(User).order_by(User.id).all()
# print ret

# ret = session.query(User).order_by(User.id)[1:3]
# print ret
# session.commit()