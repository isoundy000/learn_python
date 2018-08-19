# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_gang2_role(Base):
    __tablename__ = "t_gang2_role"
    rid = Column(Integer, primary_key=True)
    gid = Column(Integer, nullable=True, default=None)
    point = Column(Integer, nullable=False, default=0)
    pointtoday = Column(Integer, nullable=False, default=0)
    pointtotal = Column(Integer, nullable=False, default=0)
    status = Column(Enum('none','normal','kick','quit'), nullable=False, default='none')
    time = Column(TIMESTAMP, nullable=True, default=None)

    c1 = Column(Integer, nullable=False, default=0)#上香 0未上香 123上香
    c2 = Column(Integer, nullable=False, default=0)#每日奖励
    c3 = Column(Integer, nullable=False, default=0)#每日鱼塘喂鱼次数
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    c6 = Column(Integer, nullable=False, default=0)#鱼塘喂鱼次数
    c7 = Column(Integer, nullable=False, default=0)#上香次数
    c8 = Column(Integer, nullable=False, default=0)#喂鱼贡献度
    c9 = Column(Integer, nullable=False, default=0)
    c10 = Column(Integer, nullable=False, default=0)
    c11 = Column(Integer, nullable=False, default=0)
    c12 = Column(Integer, nullable=False, default=0)
    c13 = Column(Integer, nullable=False, default=0)
    c14 = Column(Integer, nullable=False, default=0)
    c15 = Column(Integer, nullable=False, default=0)
    c16 = Column(Integer, nullable=False, default=0)
    c17 = Column(Integer, nullable=False, default=0)
    c18 = Column(Integer, nullable=False, default=0)
    c19 = Column(Integer, nullable=False, default=0)
    c20 = Column(Integer, nullable=False, default=0)
    c21 = Column(Integer, nullable=False, default=0)
    c22 = Column(Integer, nullable=False, default=0)
    c23 = Column(Integer, nullable=False, default=0)
    c24 = Column(Integer, nullable=False, default=0)
    c25 = Column(Integer, nullable=False, default=0)
    c26 = Column(Integer, nullable=False, default=0)
    c27 = Column(Integer, nullable=False, default=0)
    c28 = Column(Integer, nullable=False, default=0)
    c29 = Column(Integer, nullable=False, default=0)
    c30 = Column(Integer, nullable=False, default=0)

    r1 = Column(Enum('no','yes','get'), nullable=False, default='no')#鱼塘进度条1
    r2 = Column(Enum('no','yes','get'), nullable=False, default='no')#鱼塘进度条2
    r3 = Column(Enum('no','yes','get'), nullable=False, default='no')#鱼塘进度条3
    r4 = Column(Enum('no','yes','get'), nullable=False, default='no')#鱼塘进度条4
    r5 = Column(Enum('no','yes','get'), nullable=False, default='no')
    r6 =  Column(Enum('no','yes','get'), nullable=False, default='no') #公会膜拜进度条1
    r7 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')#公会膜拜进度条2
    r8 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')#公会膜拜进度条3
    r9 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')#公会膜拜进度条4
    r10 = Column(Enum('no', 'yes', 'get'), nullable=False, default='no')#公会膜拜进度条5


    gpid = Column(Integer, nullable=True, default=None)
    gptime = Column(TIMESTAMP, nullable=True, default=None)
    gprewards = Column(String, nullable=True, default=None)
    gprewardstatus = Column(Enum("yes","no","get"), nullable=True, default="no")

    inspire1atk = Column(Integer, nullable=True, default=0)
    inspire1def = Column(Integer, nullable=True, default=0)
    inspire2    = Column(Integer, nullable=True, default=0)

    bossnum = Column(Integer, nullable=True, default=0)  # 可挑战次数
    bosspoint = Column(Integer, nullable=True, default=0)  # 贡献度


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid', 'gid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj