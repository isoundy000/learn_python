#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, TIMESTAMP
Base = declarative_base()

from Source.DataBase.Common.DBEngine import session_scope


class t_ktime(Base):

    __tablename__ = 't_ktime'
    __table_args__ = {'extend_existing': True}

    key = Column(String, primary_key=True)
    time = Column(TIMESTAMP, nullable=False, default=datetime.now)

    @staticmethod
    def LoadAllToDict():
        ret = {}
        with session_scope() as session:
            result = session.query(t_ktime).all()
            if result:
                for r in result:
                    ret[r.key] = r
        return ret