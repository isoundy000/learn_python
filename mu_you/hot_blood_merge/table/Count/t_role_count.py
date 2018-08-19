# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


#c15 每日获得体力数
#c16 每日好友副本助攻次数

#c49上一天助攻次数
#c50月卡计数 ok

#c31 累计充值金额 ok
#c32 合成绿色宝物个数 ok
#c33 合成蓝色宝物个数 ok
#c34 合成紫色宝物个数 ok
#c35 合成橙色宝物个数 ok
#c36 群仙屠龙总伤害值 ok
#c37 获得蓝色命格个数 ok
#c38 获得紫色命格个数 ok
#c39 获得橙色命格个数 ok
#c40 诛仙台元宝重置次数 ok
#c41 累计使用元宝挑战好友副本次数
#c42 世界boss最好名次
#c43 杯赛最高名次

class t_role_count(Base):
    __tablename__ = "t_role_count"
    rid = Column(Integer, primary_key=True)
    c1 = Column(Integer, nullable=True, default=0)
    c2 = Column(Integer, nullable=True, default=0)
    c3 = Column(Integer, nullable=True, default=0)
    c4 = Column(Integer, nullable=True, default=0)
    c5 = Column(Integer, nullable=True, default=0)
    c6 = Column(Integer, nullable=True, default=0)
    c7 = Column(Integer, nullable=True, default=0)
    c8 = Column(Integer, nullable=True, default=0)
    c9 = Column(Integer, nullable=True, default=0)
    c10 = Column(Integer, nullable=True, default=0)
    c11 = Column(Integer, nullable=True, default=0)
    c12 = Column(Integer, nullable=True, default=0)
    c13 = Column(Integer, nullable=True, default=0)
    c14 = Column(Integer, nullable=True, default=0)
    c15 = Column(Integer, nullable=True, default=0)
    c16 = Column(Integer, nullable=True, default=0)
    c17 = Column(Integer, nullable=True, default=0)
    c18 = Column(Integer, nullable=True, default=0)
    c19 = Column(Integer, nullable=True, default=0)
    c20 = Column(Integer, nullable=True, default=0)
    c21 = Column(Integer, nullable=True, default=0)
    c22 = Column(Integer, nullable=True, default=0)
    c23 = Column(Integer, nullable=True, default=0)# 锻造石副本累计攻打次数
    c24 = Column(Integer, nullable=True, default=0)
    c25 = Column(Integer, nullable=True, default=0)
    c26 = Column(Integer, nullable=True, default=0)
    c27 = Column(Integer, nullable=True, default=0)
    c28 = Column(Integer, nullable=True, default=0)
    c29 = Column(Integer, nullable=True, default=0)
    c30 = Column(Integer, nullable=True, default=0)
    c31 = Column(Integer, nullable=True, default=0)
    c32 = Column(Integer, nullable=True, default=0)
    c33 = Column(Integer, nullable=True, default=0)
    c34 = Column(Integer, nullable=True, default=0)
    c35 = Column(Integer, nullable=True, default=0)
    c36 = Column(Integer, nullable=True, default=0)
    c37 = Column(Integer, nullable=True, default=0)
    c38 = Column(Integer, nullable=True, default=0)
    c39 = Column(Integer, nullable=True, default=0)
    c40 = Column(Integer, nullable=True, default=0)
    c41 = Column(Integer, nullable=True, default=0)
    c42 = Column(Integer, nullable=True, default=0)
    c43 = Column(Integer, nullable=True, default=0)
    c44 = Column(Integer, nullable=True, default=0)
    c45 = Column(Integer, nullable=True, default=0)
    c46 = Column(Integer, nullable=True, default=0)
    c47 = Column(Integer, nullable=True, default=0)
    c48 = Column(Integer, nullable=True, default=0)
    c49 = Column(Integer, nullable=True, default=0)
    c50 = Column(Integer, nullable=True, default=0)
    c51 = Column(Integer, nullable=True, default=0)
    c52 = Column(Integer, nullable=True, default=0)
    c53 = Column(Integer, nullable=True, default=0)
    c54 = Column(Integer, nullable=True, default=0)
    c55 = Column(Integer, nullable=True, default=0)
    c56 = Column(Integer, nullable=True, default=0)
    c57 = Column(Integer, nullable=True, default=0)
    c58 = Column(Integer, nullable=True, default=0)
    c59 = Column(Integer, nullable=True, default=0)
    c60 = Column(Integer, nullable=True, default=0)
    c61 = Column(Integer, nullable=True, default=0)
    c62 = Column(Integer, nullable=True, default=0)
    c63 = Column(Integer, nullable=True, default=0)
    c64 = Column(Integer, nullable=True, default=0)
    c65 = Column(Integer, nullable=True, default=0)
    c66 = Column(Integer, nullable=True, default=0)
    c67 = Column(Integer, nullable=True, default=0)
    c68 = Column(Integer, nullable=True, default=0)
    c69 = Column(Integer, nullable=True, default=0)
    c70 = Column(Integer, nullable=True, default=0)



    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
