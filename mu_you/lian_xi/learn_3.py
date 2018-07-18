# -*- encoding: utf-8 -*-
'''
Created on 2018年4月10日

@author: houguangdong
'''
# 1.版本检查
import sqlalchemy
# sqlalchemy.__version__

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import aliased
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import text
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationships, backref
from sqlalchemy import connectors
from random import randint


# 创建实例， 并连接dong库
engine = create_engine('mysql+mysqldb://sanguo_bg:sanguo_passwd@localhost:3306/ghou', encoding='utf-8', echo=True)
Session = sessionmaker(bind=engine)

Session = Session()
# echo=True显示信息
Base = declarative_base()


class t_activity_may_first(Base):
    '''
    5月1活动
    '''

    __tablename__ = 't_activity_may_first'

    rid = Column(Integer, primary_key=True)
    day1 = Column(Integer, nullable=False, default=0)           # 每日登陆
    day2 = Column(Integer, nullable=False, default=0)           # 1激活奖励 2领取奖励
    day3 = Column(Integer, nullable=False, default=0)
    day4 = Column(Integer, nullable=False, default=0)
    day5 = Column(Integer, nullable=False, default=0)
    day6 = Column(Integer, nullable=False, default=0)
    day7 = Column(Integer, nullable=False, default=0)

    recharge = Column(Integer, nullable=False, default=0)       # 累计充值
    r1 = Column(Integer, nullable=False, default=0)             # 1激活奖励 2领取奖励
    r2 = Column(Integer, nullable=False, default=0)
    r3 = Column(Integer, nullable=False, default=0)
    r4 = Column(Integer, nullable=False, default=0)
    r5 = Column(Integer, nullable=False, default=0)
    r6 = Column(Integer, nullable=False, default=0)
    r7 = Column(Integer, nullable=False, default=0)
    r8 = Column(Integer, nullable=False, default=0)
    r9 = Column(Integer, nullable=False, default=0)

    challenges = Column(Integer, nullable=False, default=0)     # 挑战次数
    c1 = Column(Integer, nullable=False, default=0)             # 1激活奖励 2领取奖励
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    c6 = Column(Integer, nullable=False, default=0)
    c7 = Column(Integer, nullable=False, default=0)
    c8 = Column(Integer, nullable=False, default=0)
    c9 = Column(Integer, nullable=False, default=0)
    c10 = Column(Integer, nullable=False, default=0)

    s1 = Column(Integer, nullable=False, default=0)             # 兑换次数
    s2 = Column(Integer, nullable=False, default=0)
    s3 = Column(Integer, nullable=False, default=0)
    s4 = Column(Integer, nullable=False, default=0)
    s5 = Column(Integer, nullable=False, default=0)
    s6 = Column(Integer, nullable=False, default=0)
    s7 = Column(Integer, nullable=False, default=0)
    s8 = Column(Integer, nullable=False, default=0)
    s9 = Column(Integer, nullable=False, default=0)
    s10 = Column(Integer, nullable=False, default=0)
    s11 = Column(Integer, nullable=False, default=0)
    s12 = Column(Integer, nullable=False, default=0)
    s13 = Column(Integer, nullable=False, default=0)
    s14 = Column(Integer, nullable=False, default=0)