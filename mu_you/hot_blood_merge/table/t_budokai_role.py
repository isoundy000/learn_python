# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_budokai_role(Base):
    __tablename__ = 't_budokai_role'

    rid = Column(Integer, primary_key=True)

    init = Column(Boolean, nullable=False, default=False)

    camp = Column(Integer, nullable=True, default=None)         # 阵营
    point = Column(Integer, nullable=False, default=0)          # 当前积分
    total_point = Column(Integer, nullable=False, default=0)    # 总积分
    this_point = Column(Integer, nullable=False, default=0)     # 本次活动积分
    count = Column(Integer, nullable=False, default=0)          # 战斗次数
    win_count = Column(Integer, nullable=False, default=0)      # 战斗胜利次数
    succ_win_count = Column(Integer, nullable=False, default=0) # 连续胜利次数
    match_count = Column(Integer, nullable=False, default=0)    # 匹配未中次数
    last_rank = Column(Integer, nullable=True, default=None)    # 上次活动排名
    lottery_count = Column(Integer, nullable=False, default=0)  # 抽奖次数

    s1 = Column(Integer, nullable=False, default=0)             # 1胜宝箱  0: 未达到条件 1: 可领取 2: 已经领取
    s5 = Column(Integer, nullable=False, default=0)             # 5胜宝箱
    s10 = Column(Integer, nullable=False, default=0)            # 10战宝箱

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
