# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_olduser_return(Base):
    __tablename__ = 't_olduser_return'
    rid = Column(Integer, primary_key=True)
    sta = Column(Integer, nullable=False, default=0)  # 回归玩家类型
    iscode = Column(Integer, nullable=False, default=0)  # 是否使用过召回码
    ft = Column(Integer, nullable=False, default=1)  # 是否当天首次登陆（1是，0否）
    days = Column(Integer, nullable=False, default=0)  # 累计登陆天数
    sr = Column(Integer, nullable=False, default=0)  # 单日充值
    tr = Column(Integer, nullable=False, default=0)  # 累计充值
    t1 = Column(Enum("yes","no","get"), nullable=True, default="no") # 前三个标签页 按钮状态
    t2 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t3 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t4 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t5 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t6 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t7 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t8 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t9 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t10 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t11 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t12 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t13 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t14 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t15 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t16 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t17 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t18 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t19 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t20 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t21 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t22 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t23 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t24 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t25 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t26 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t27 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t28 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t29 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t30 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t31 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t32 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t33 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t34 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t35 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t36 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t37 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t38 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t39 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t40 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t41 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t42 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t43 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t44 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t45 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t46 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t47 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t48 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t49 = Column(Enum("yes","no","get"), nullable=True, default="no")
    t50 = Column(Enum("yes","no","get"), nullable=True, default="no")
    c1 = Column(Integer, nullable=False, default=0)  # 超值购买已购买次数
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
    c21 = Column(Integer, nullable=False, default=0)
    c22 = Column(Integer, nullable=False, default=0)
    c23 = Column(Integer, nullable=False, default=0)
    c24 = Column(Integer, nullable=False, default=0)
    c25 = Column(Integer, nullable=False, default=0)
    c26 = Column(Integer, nullable=False, default=0)
    c27 = Column(Integer, nullable=False, default=0)
    c28 = Column(Integer, nullable=False, default=0)
    c29 = Column(Integer, nullable=False, default=0)
    c30 = Column(Integer, nullable=False, default=0)

    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj