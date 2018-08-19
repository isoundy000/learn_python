# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_recharge_monthcard(Base):
    __tablename__ = 't_recharge_monthcard'
    rid = Column(Integer, primary_key=True)
    day1 = Column(Integer, nullable=False, default=0)
    status1 = Column(Enum('yes','no', 'get'),nullable=False, default='no')
    day2 = Column(Integer, nullable=False, default=0)
    status2 = Column(Enum('yes','no', 'get'),nullable=False, default='no')
    rmb = Column(Integer, nullable=False, default=0)
    r1 = Column(Enum('yes','no', 'get'),nullable=False, default="no")
    r2 = Column(Enum('yes','no', 'get'),nullable=False, default="no")
    r3 = Column(Enum('yes','no', 'get'),nullable=False, default="no")
    r4 = Column(Enum('yes','no', 'get'),nullable=False, default="no")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj