# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_recruit_priority(Base):
    __tablename__ = "t_recruit_priority"
    rid = Column(Integer, primary_key=True, nullable=False)
    counter = Column(Integer, primary_key=True, nullable=False)
    priority = Column(Integer, primary_key=True, nullable=False)
    c1 = Column(Integer, nullable=False, default=0)#激活次数
    c2 = Column(Integer, nullable=False, default=0)#激活状态中次数
    c3 = Column(Integer, nullable=False, default=0)
    c4 = Column(Integer, nullable=False, default=0)
    c5 = Column(Integer, nullable=False, default=0)#消费数量

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj