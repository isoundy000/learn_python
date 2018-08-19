# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_recruit_counter(Base):
    __tablename__ = "t_recruit_counter"
    rid = Column(Integer, primary_key=True, nullable=False)
    counter = Column(Integer, primary_key=True, nullable=False)
    c1 = Column(Integer, nullable=False, default=0)#计数器
    c2 = Column(Integer, nullable=False, default=0)#免费抽奖次数
    c3 = Column(Integer, nullable=False, default=0)#消费抽奖次数
    c4 = Column(Integer, nullable=False, default=0)#十连抽次数
    c5 = Column(Integer, nullable=False, default=0)
    c6 = Column(Integer, nullable=False, default=0)
    c7 = Column(Integer, nullable=False, default=0)
    c8 = Column(Integer, nullable=False, default=0)
    c9 = Column(Integer, nullable=False, default=0)
    c10 = Column(Integer, nullable=False, default=0)
    time = Column(TIMESTAMP, nullable=True, default=None)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj