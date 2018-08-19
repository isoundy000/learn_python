#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_general4(Base):
    __tablename__ = 't_general4'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    rid = Column(Integer, nullable=False)
    cid = Column(Integer, nullable=False)                   # 武将 generalid
    level1 = Column(Integer, nullable=False)                # 武将等级
    level2 = Column(Integer, nullable=False)                # 突破等级
    exp = Column(Integer, nullable=True, default=0)         # 武将经验
    hp_foster = Column(Integer, nullable=True, default=0)   # 培养属性 攻击
    atk_foster = Column(Integer, nullable=True, default=0)
    def_foster = Column(Integer, nullable=True, default=0)

    potential = Column(Integer, nullable=False, default=0)  # 潜力点(增加 atk, def, hp, speed)

    weapon = Column(Integer, nullable=True, default=None)
    armor = Column(Integer, nullable=True, default=None)
    accessory = Column(Integer, nullable=True, default=None)
    head = Column(Integer, nullable=True, default=None)
    treasure = Column(Integer, nullable=True, default=None)     # 宝物
    horse = Column(Integer, nullable=True, default=None)        # 宝物

    s1 = Column(Integer, nullable=True, default=None)           # 武魂就是命格
    s2 = Column(Integer, nullable=True, default=None)
    s3 = Column(Integer, nullable=True, default=None)
    s4 = Column(Integer, nullable=True, default=None)
    s5 = Column(Integer, nullable=True, default=None)
    s6 = Column(Integer, nullable=True, default=None)
    s7 = Column(Integer, nullable=True, default=None)
    s8 = Column(Integer, nullable=True, default=None)

    skillexp = Column(Integer, nullable=False, default=0)
    skilllevel = Column(Integer, nullable=False, default=0)

    power = Column(Integer, nullable=True, default=0)   # 战斗力

    level3 = Column(Integer, nullable=True, default=0)  # 觉醒等级
    level4 = Column(Integer, nullable=True, default=0)  # 进阶等级

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj