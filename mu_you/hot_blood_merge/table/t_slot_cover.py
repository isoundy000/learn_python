#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'jutian'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_slot_cover(Base):
    __tablename__ = "t_slot_cover"
    __table_args__ = {'extend_existing':True}
    rid = Column(Integer, primary_key=True)

    l1 = Column(Integer, nullable=False, default=0) # 等级
    l2 = Column(Integer, nullable=False, default=0)
    l3 = Column(Integer, nullable=False, default=0)
    l4 = Column(Integer, nullable=False, default=0)
    l5 = Column(Integer, nullable=False, default=0)
    l6 = Column(Integer, nullable=False, default=0)
    l7 = Column(Integer, nullable=False, default=0)

    t1 = Column(Integer, nullable=False, default=0) # 成就（记录现已完成的最高成就）
    t2 = Column(Integer, nullable=False, default=0)
    t3 = Column(Integer, nullable=False, default=0)
    t4 = Column(Integer, nullable=False, default=0)
    t5 = Column(Integer, nullable=False, default=0)
    t6 = Column(Integer, nullable=False, default=0)
    t7 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj