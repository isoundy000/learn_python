#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
Base = declarative_base()

from Source.DataBase.Common.DBEngine import session_scope
from Source.Log.Write import Log


class t_system_params(Base):

    __tablename__ = 't_system_params'

    key = Column(String, primary_key=True)
    value = Column(String, nullable=True, default=None)

    @staticmethod
    def LoadAll():
        result = []
        with session_scope() as session:
            notices = session.query(t_system_params).all()
        for notice in notices:
            result[notice.key] = notice
        return result

    @staticmethod
    def LoadParamBykey(key):
        '''
        通过key获取参数value的值
        :param key:
        :return:
        '''
        result = None
        value = None
        with session_scope() as session:
            result = session.query(t_system_params).filter(t_system_params.key == key).first()
        if result:
            value = result.value
        Log.Write("SystemParam.get", key, value)
        return value