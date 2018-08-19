# -*- coding: UTF-8 -*-
# !/usr/bin/env python

__author__ = 'liuzhaoyang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
Base = declarative_base()


class t_facebook(Base):
    __tablename__ = 't_facebook'

    rid = Column(Integer, primary_key=True)
    c1 = Column(Integer, nullable=False, default=0) # 赞
    c2 = Column(Integer, nullable=False, default=0) # 分享
    c3 = Column(Integer, nullable=False, default=0) # 绑定
    c4 = Column(Integer, nullable=False, default=0) # 分享活动 是否分享
    c5 = Column(Integer, nullable=False, default=0) # 分享活动 是否领取
    c6 = Column(Integer, nullable=False, default=0) # 邀请活动
    c7 = Column(Integer, nullable=False, default=0)
    c8 = Column(Integer, nullable=False, default=0)
    c9 = Column(Integer, nullable=False, default=0)
    c10 = Column(Integer, nullable=False, default=0)


    @classmethod
    def new_from(cls, obj):
        new_obj = cls()
        for attr_name in cls._sa_class_manager.keys():
            if attr_name not in ['id', 'rid']:
                setattr(new_obj, attr_name, getattr(obj, attr_name))
        return new_obj