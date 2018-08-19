#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()
from datetime import datetime


class t_manor(Base):
    __tablename__ = "t_manor"
    rid = Column(Integer, primary_key=True)
    wood = Column(Integer, nullable=True, default=0)  # 木材产出
    maxwood = Column(Integer, nullable=True, default=0)  # 木材产出存储上限
    stone = Column(Integer, nullable=True, default=0)  # 石料产出
    maxstone = Column(Integer, nullable=True, default=0)  # 石料产出存储上限
    content = Column(String, nullable=True, default=None)  # 气泡
    time = Column(TIMESTAMP, nullable=False, default=datetime.now)  # 任务栏升阶时间
    t1 = Column(Integer, nullable=False, default=0)  # 任务一id
    t2 = Column(Integer, nullable=False, default=0)  # 任务二id
    t3 = Column(Integer, nullable=False, default=0)  # 任务三id
    s1 = Column(Integer, nullable=False, default=0)  # 任务一状态
    s2 = Column(Integer, nullable=False, default=0)  # 任务二状态
    s3 = Column(Integer, nullable=False, default=0)  # 任务三状态
    n1 = Column(Integer, nullable=False, default=0)  # 任务一进度
    n2 = Column(Integer, nullable=False, default=0)  # 任务二进度
    n3 = Column(Integer, nullable=False, default=0)  # 任务三进度
    c1 = Column(Integer, nullable=False, default=0)  # 小妖1（0无，1有）
    c2 = Column(Integer, nullable=False, default=0)  # 小妖2
    c3 = Column(Integer, nullable=False, default=0)  # 作妖剩余
    c4 = Column(Integer, nullable=False, default=0)  # 任务刷新次数
    c5 = Column(Integer, nullable=False, default=0)  # 完成任务次数
    c6 = Column(Integer, nullable=False, default=0)  # 木材未领取次数
    c7 = Column(Integer, nullable=False, default=0)  # 石料未领取次数
    c8 = Column(Integer, nullable=False, default=0)  # 是否增加小妖标识(0否,1是)
    c9 = Column(Integer, nullable=False, default=0)
    c10 = Column(Integer, nullable=False, default=0)
    c11 = Column(Integer, nullable=False, default=0)  # 0点刷新标识
    c12 = Column(Integer, nullable=False, default=0)
    c13 = Column(Integer, nullable=False, default=0)
    c14 = Column(Integer, nullable=False, default=0)
    c15 = Column(Integer, nullable=False, default=0)
    b1level1 = Column(Integer, nullable=False, default=0)  # 建筑1等级
    b1level2 = Column(Integer, nullable=False, default=0)  # 建筑1品质
    b2level1 = Column(Integer, nullable=False, default=0)
    b2level2 = Column(Integer, nullable=False, default=0)
    b3level1 = Column(Integer, nullable=False, default=0)
    b3level2 = Column(Integer, nullable=False, default=0)
    b4level1 = Column(Integer, nullable=False, default=0)
    b4level2 = Column(Integer, nullable=False, default=0)
    b5level1 = Column(Integer, nullable=False, default=0)
    b5level2 = Column(Integer, nullable=False, default=0)
    b6level1 = Column(Integer, nullable=False, default=0)
    b6level2 = Column(Integer, nullable=False, default=0)
    b7level1 = Column(Integer, nullable=False, default=0)
    b7level2 = Column(Integer, nullable=False, default=0)
    b8level1 = Column(Integer, nullable=False, default=0)
    b8level2 = Column(Integer, nullable=False, default=0)
    b9level1 = Column(Integer, nullable=False, default=0)
    b9level2 = Column(Integer, nullable=False, default=0)
    b10level1 = Column(Integer, nullable=False, default=0)
    b10level2 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj