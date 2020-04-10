#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String
Base = declarative_base()
from Source.DataBase.Common.DBEngine import DBEngine, session_scope
from Source.Log.Write import Log


class t_session(Base):
    '''session记录'''
    __tablename__ = "t_session"

    uid = Column(Integer, primary_key=True)                     # uid
    uuid = Column(String, nullable=False)                       # sid
    server = Column(Integer, nullable=True, default=None)

    @staticmethod
    def Update(uid, uuid, server=None):
        Log.Write("t_session", uid, uuid)
        with session_scope() as session:
            result = session.query(t_session).filter(t_session.uid == uid).first()
            if result is None:
                result = t_session()
                result.uid = uid
                result.uuid = uuid
                result.server = server
                DBEngine.Add(result)
            else:
                result.uuid = uuid
                result.server = server
                DBEngine.Update(result)

    @staticmethod
    def Find(uuid):
        with session_scope() as session:
            result = session.query(t_session).filter(t_session.uuid == uuid).first()
        return result