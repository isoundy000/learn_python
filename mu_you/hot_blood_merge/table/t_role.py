# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_role(Base):

    __tablename__ = 't_role'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, nullable=False)
    gender = Column(Enum("male", "female"), nullable=True, default="male")
    name = Column(String, nullable=True, default="")
    vip = Column(Integer, nullable=False, default=0)
    level = Column(Integer, nullable=False, default=1)
    exp = Column(Integer, nullable=False, default=0)
    coin = Column(Integer, nullable=False, default=0)
    gold = Column(Integer, nullable=False, default=100000)
    stamina = Column(Integer, nullable=False)                           # 体力
    maxstamina = Column(Integer, nullable=False, default=100)
    energy = Column(Integer, nullable=False)                            # 精力
    maxenergy = Column(Integer, nullable=False, default=100)
    prestige = Column(Integer, nullable=False, default=0)               # 竞技场积分
    athletics = Column(Integer, nullable=False, default=3)              # 竞技场剩余的次数
    createtime = Column(TIMESTAMP, nullable=False)                      # 建角时间
    maxfriend = Column(Integer, nullable=True, default=10)
    profile = Column(Integer, nullable=True, default=None)              # 头像标识
    channel = Column(String, nullable=True, default=None)
    power = Column(Integer, nullable=True, default=0)
    platform = Column(Enum('ios', 'android'), nullable=True, default=None)
    lastlogin = Column(TIMESTAMP, nullable=True, default=None)          # 最后一次登陆的时间
    avatar = Column(Integer, nullable=False, default=0)                 # 头像框
    lang = Column(String, nullable=True, default="CN")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
