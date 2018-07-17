# -*- encoding: utf-8 -*-
'''
Created on 2018年4月10日

@author: houguangdong
'''
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String


# 创建实例， 并连接dong库
engine = create_engine('mysql+mysqldb://root:donga123@localhost:3306/dong')

# echo=True显示信息
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'  # 表名
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    password = Column(String(64))



if __name__ == '__main__':
    Base.metadata.create_all(engine) #创建表结构 （这里是父类调子类）