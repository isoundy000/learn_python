# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class t_god_down_x6(Base):
    __tablename__ = 't_god_down_x6'
    rid = Column(Integer, primary_key=True)
    gift_box_status = Column(Integer, nullable=False, default=0)  # 0: 未领取 1: 已领取
    tribute_cfg_id = Column(Integer, nullable=True, default=None)
    tribute_dt = Column(TIMESTAMP, nullable=True, default=None)
    total_point = Column(Integer, nullable=False, default=0)
    point = Column(Integer, nullable=False, default=0)
    c1 = Column(Integer, nullable=False, default=0)  # 兑换次数
    c2 = Column(Integer, nullable=False, default=0)
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)
    c6 = Column(Integer, nullable=False, default=0)
    c7 = Column(Integer, nullable=False, default=0)
    c8 = Column(Integer, nullable=False, default=0)
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

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
