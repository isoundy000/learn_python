# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_time_gift(Base):
    __tablename__ = 't_time_gift'
    rid = Column(Integer, primary_key=True)
    r1 = Column(Enum('yes', 'no', 'get'), nullable=False, default="no")  # 周礼包按钮状态
    r2 = Column(Enum('yes', 'no', 'get'), nullable=False, default="no")  # 月礼包按钮状态
    c1 = Column(Integer, nullable=False, default=1)  # 周礼包档位
    c2 = Column(Integer, nullable=False, default=1)  # 月礼包档位

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj
