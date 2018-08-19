# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_god_down(Base):

    __tablename__ = 't_god_down'
    rid = Column(Integer, primary_key=True)
    gift_box_status = Column(Integer, nullable=False, default=0)    # 0: 未领取 1: 已领取
    tribute_cfg_id = Column(Integer, nullable=True, default=None)   # 圆梦方式 1普通 2中级 3高级
    tribute_dt = Column(TIMESTAMP, nullable=True, default=None)     # 圆梦时间
    total_point = Column(Integer, nullable=False, default=0)        # 总好感度
    point = Column(Integer, nullable=False, default=0)              # 好感度
    c1 = Column(Integer, nullable=False, default=0)                 # 商场兑换的礼品 兑换次数
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    c6 = Column(Integer, nullable=False, default=0)
    c7 = Column(Integer, nullable=False, default=0)
    c8 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
