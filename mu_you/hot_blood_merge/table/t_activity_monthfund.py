# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_activity_monthfund(Base):
    __tablename__ = 't_activity_monthfund'
    rid = Column(Integer, primary_key=True)
    status = Column(Integer, nullable=False, default=0)#0 活动未开启 1活动开启
    s1 = Column(Enum("no","yes","get"), nullable=False, default="no")
    s2 = Column(Enum("no","yes","get"), nullable=False, default="no")
    s3 = Column(Enum("no","yes","get"), nullable=False, default="no")
    s4 = Column(Enum("no","yes","get"), nullable=False, default="no")
    days1 = Column(Integer, nullable=False, default=0)
    days2 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj