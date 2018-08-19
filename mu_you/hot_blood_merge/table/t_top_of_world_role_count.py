# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'yanglei'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()

class t_top_of_world_role_count(Base):
    # 走向巅峰任务进度记录表
    __tablename__ = 't_top_of_world_role_count'
    rid = Column(Integer, primary_key=True)
    days = Column(Integer, nullable=True, default=0)  # 28天经历天数
    tag = Column(Integer, nullable=True, default=0)  # 刷新标志
    lastlogin = Column(TIMESTAMP, nullable=True, default=None)
    c1 = Column(Integer, nullable=True, default=0)
    c2 = Column(Integer, nullable=True, default=0)   # 累计充值钱数
    c3 = Column(Integer, nullable=True, default=0)
    c4 = Column(Integer, nullable=True, default=0)
    c5 = Column(Integer, nullable=True, default=0)
    c6 = Column(Integer, nullable=True, default=0)
    c7 = Column(Integer, nullable=True, default=0)   # 合成蓝色宝物个数
    c8 = Column(Integer, nullable=True, default=0)   # 圣兽降临总伤害通知
    c9 = Column(Integer, nullable=True, default=0)   # 合成紫色宝物个数
    c10 = Column(Integer, nullable=True, default=0)
    c11 = Column(Integer, nullable=True, default=0)
    c12 = Column(Integer, nullable=True, default=0)
    c13 = Column(Integer, nullable=True, default=0)  # 伙伴总突破次数
    c14 = Column(Integer, nullable=True, default=0)
    c15 = Column(Integer, nullable=True, default=0)  # 古渊最高层数
    c16 = Column(Integer, nullable=True, default=0)
    c17 = Column(Integer, nullable=True, default=0)
    c18 = Column(Integer, nullable=True, default=0)  # 累计挑战好友副本次数
    c19 = Column(Integer, nullable=True, default=0)  # 装备累计洗练次数
    c20 = Column(Integer, nullable=True, default=0)  # 主角进阶次数
    c21 = Column(Integer, nullable=True, default=0)
    c22 = Column(Integer, nullable=True, default=0)
    c23 = Column(Integer, nullable=True, default=0)  # 战队等级
    c24 = Column(Integer, nullable=True, default=0)  # 战斗力总和
    c25 = Column(Integer, nullable=True, default=0)
    c26 = Column(Integer, nullable=True, default=0)  # 社团祭拜次数
    c27 = Column(Integer, nullable=True, default=0)
    c28 = Column(Integer, nullable=True, default=0)
    c29 = Column(Integer, nullable=True, default=0)
    c30 = Column(Integer, nullable=True, default=0)  # 普通副本挑战次数
    c31 = Column(Integer, nullable=True, default=0)  # 精英副本胜利次数
    c32 = Column(Integer, nullable=True, default=0)  # 古渊重置次数
    c33 = Column(Integer, nullable=True, default=0)  # 十二生肖胜利次数
    c34 = Column(Integer, nullable=True, default=0)  # 神的试炼胜利次数
    c35 = Column(Integer, nullable=True, default=0)
    c36 = Column(Integer, nullable=True, default=0)  # 地下拳赛挑战次数
    c37 = Column(Integer, nullable=True, default=0)  # 夺宝次数
    c38 = Column(Integer, nullable=True, default=0)  # 竞技场挑战次数
    c39 = Column(Integer, nullable=True, default=0)
    c40 = Column(Integer, nullable=True, default=0)  # 勇士培养次数
    c41 = Column(Integer, nullable=True, default=0)  # 经验副本胜利次数
    c42 = Column(Integer, nullable=True, default=0)  # 百花坊红玫瑰送花次数
    c43 = Column(Integer, nullable=True, default=0)  # 佰花坊蓝色妖姬送花次数
    c44 = Column(Integer, nullable=True, default=0)  # 公会boss挑战次数
    c45 = Column(Integer, nullable=True, default=0)  # 荣耀对决次数
    c46 = Column(Integer, nullable=True, default=0)
    c47 = Column(Integer, nullable=True, default=0)
    c48 = Column(Integer, nullable=True, default=0)  # 观星次数
    c49 = Column(Integer, nullable=True, default=0)  # 生命古树使用次数
    c50 = Column(Integer, nullable=True, default=0)  # 杯赛押注次数
    c51 = Column(Integer, nullable=True, default=0)
    c52 = Column(Integer, nullable=True, default=0)
    c53 = Column(Integer, nullable=True, default=0)  # 圣兽降临次数
    c54 = Column(Integer, nullable=True, default=0)
    c55 = Column(Integer, nullable=True, default=0)
    c56 = Column(Integer, nullable=True, default=0)
    c57 = Column(Integer, nullable=True, default=0)
    c58 = Column(Integer, nullable=True, default=0)
    c59 = Column(Integer, nullable=True, default=0)
    c60 = Column(Integer, nullable=True, default=0)  # 勇者之间收获次数
    c61 = Column(Integer, nullable=True, default=0)  # 勇者之间完成任务次数
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

