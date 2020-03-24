#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Enum
Base = declarative_base()

from Source.DataBase.Common.DBEngine import session_scope


class t_ktv(Base):

    __tablename__ = 't_ktv'
    __table_args__ = {'extend_existing': True}  # 已为此MetaData实例定义表't_ktv'。指定“ extend_existing = True”以重新定义现有Table对象上的选项和列。
    key = Column(String, primary_key=True)                                              # section
    type = Column(Enum('string', 'int', 'float'), nullable=False, default='string')     # int
    value = Column(String, nullable=True, default=None)                                 # 3

    @staticmethod
    def LoadAllToDict():
        ret = {}
        with session_scope() as session:
            result = session.query(t_ktv).all()
            if result:
                for r in result:
                    ret[r.key] = r
        return ret