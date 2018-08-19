# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()

class t_overpass(Base):
    __tablename__ = 't_overpass'
    rid = Column(Integer, primary_key=True)
    p1 =  Column(Integer, nullable=True, default=None)  # 对手1rid
    p2 =  Column(Integer, nullable=True, default=None)  # 对手2rid
    p3 =  Column(Integer, nullable=True, default=None)  # 对手3rid
    point_week = Column(Integer, nullable=False, default=0)  # 斩将积分
    point_left = Column(Integer, nullable=False, default=0)  # 斩将币
    c1 =  Column(Integer, nullable=False, default=0)  # 对手1 攻打状态（0未击败，1击败）
    c2 =  Column(Integer, nullable=False, default=0)  # 对手2 攻打状态
    c3 =  Column(Integer, nullable=False, default=0)  # 对手3 攻打状态
    c4 =  Column(Integer, nullable=False, default=0)  # 战胜次数
    c5 =  Column(Integer, nullable=False, default=0)  # 刷新次数
    c6 =  Column(Integer, nullable=False, default=0)  # 挑战次数
    c7 =  Column(Integer, nullable=False, default=0)
    c8 =  Column(Integer, nullable=False, default=0)
    c9 =  Column(Integer, nullable=False, default=0)
    c10 =  Column(Integer, nullable=False, default=0)
    s1 = Column(Enum("no","yes","get"), nullable=False, default="no")  # 宝箱1领取状态
    s2 = Column(Enum("no","yes","get"), nullable=False, default="no")  # 宝箱2领取状态
    s3 = Column(Enum("no","yes","get"), nullable=False, default="no")  # 宝箱3领取状态
    s4 = Column(Enum("no","yes","get"), nullable=False, default="no")
    s5 = Column(Enum("no","yes","get"), nullable=False, default="no")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name in ['point_week', 'point_left']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
