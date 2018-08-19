# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_olduser_mycode(Base):
    __tablename__ = 't_olduser_mycode'
    rid = Column(Integer, primary_key=True)
    num = Column(Integer, nullable=False, default=0)  # 召回码被使用次数
    c1 = Column(Integer, nullable=False, default=0) # 类型1奖励 已领取次数
    t1 = Column(Enum("yes","no","get"), nullable=True, default="no") # 按钮状态
    t2 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t3 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t4 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t5 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t6 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t7 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t8 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t9 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t10 = Column(Enum("yes","no","get"), nullable=True, default="no")

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj