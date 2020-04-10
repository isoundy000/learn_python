#!/usr/bin/env python
#-*- coding: UTF-8 -*-
__author__ = 'ghou'

import traceback
import gevent
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from Source.Config.ConfigManager import ConfigManager
from Source.Log.Write import Log
from sqlalchemy.sql.expression import *

@contextmanager
def session_scope2():
    """Provide a transactional scope around a series of operations."""
    session = DBEngine.NewSession()
    try:
        yield session
        session.commit()
    except Exception, e:
        Log.Write(e)
        Log.Write(traceback.format_exc())
        session.rollback()
        # raise
    finally:
        # DBEngine.DelSession(session)
        pass

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = DBEngine.NewSession()
    try:
        yield session
    except Exception, e:
        Log.Write(e)
        Log.Write(traceback.format_exc())

@contextmanager
def session_scope3():
    """Provide a transactional scope around a series of operations."""
    session = DBEngine.NewSession()
    try:
        yield session
    except Exception, e:
        Log.Write(e)
        Log.Write(traceback.format_exc())
        # raise
        pass
    finally:
        session.commit()
        # session.expunge_all()

@contextmanager
def session_scope4():
    """Provide a transactional scope around a series of operations."""
    session = DBEngine.NewSession()
    try:
        yield session
        session.commit()
    except Exception, e:
        Log.Write(e)
        Log.Write(traceback.format_exc())
        session.rollback()
        # raise
    finally:
        session.commit()
        # session.expunge_all()

@contextmanager
def session_New():
    """Provide a transactional scope around a series of operations."""
    session = DBEngine._sessionmaker()
    try:
        yield session
    except Exception, e:
        Log.Write(e)
        Log.Write(traceback.format_exc())
    finally:
        session.commit()
        session.expunge_all()
        session.close()


class DBEngine:

    _engine = None
    _sessionmaker = None
    _commonsession = None
    _geventsessions = {}

    def _init():
        configmanager = ConfigManager.Singleton()
        dbconfig = configmanager["Server"]["DataBase"]["DB1"]
        Log.Write(dbconfig)
        unix_socket = None

        if dbconfig["echo"] == "true":
            bEngineEcho = True
        else:
            bEngineEcho = False

        if "unix_socket" in dbconfig and dbconfig["unix_socket"]:
            unix_socket = dbconfig["unix_socket"]
        if unix_socket:
            conn_str = "mysql://%s:%s@/%s?%s" % (dbconfig["user"], dbconfig["password"], dbconfig["db"], dbconfig["param"])
            DBEngine._engine = create_engine(
                conn_str, echo=bEngineEcho,
                pool_size=100, max_overflow=100, pool_recycle=10*60, connect_args={'unix_socket': '%s' % (unix_socket,)})
        else:
            conn_str = "mysql://%s:%s@%s:%s/%s?%s" % (dbconfig["user"],
                                                   dbconfig["password"],
                                                   dbconfig["host"],
                                                   dbconfig["port"],
                                                   dbconfig["db"],
                                                   dbconfig["param"])
            DBEngine._engine = create_engine(conn_str, echo=bEngineEcho,
                                         pool_size=100, max_overflow=100, pool_recycle=10*60)

        Log.Write("conn_str", conn_str)
        # DBEngine._engine = create_engine(conn_str, echo=bEngineEcho,
        #   pool_size=100, max_overflow=100, pool_recycle=10*60, connect_args={'unix_socket':'/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock'})
        try:
            DBEngine._engine.connect()
        except OperationalError, e:
            Log.Write(e)
            return False

        DBEngine._sessionmaker = sessionmaker()
        DBEngine._sessionmaker.configure(bind=DBEngine._engine, autoflush=False, expire_on_commit=False)
        DBEngine._commonsession = DBEngine._sessionmaker()
        return True

    Init = staticmethod(_init)

    @staticmethod
    def Reconnect():
        try:
            DBEngine._engine.connect()
        except OperationalError, e:
            Log.Write(e)
            return False

        DBEngine._sessionmaker = sessionmaker()
        DBEngine._sessionmaker.configure(bind=DBEngine._engine, autoflush=False, expire_on_commit=False)
        DBEngine._commonsession = DBEngine._sessionmaker()

    def _newsession():
        return DBEngine._commonsession

    NewSession = staticmethod(_newsession)

    def _delsession(session):
        pass

    DelSession = staticmethod(_delsession)

    @staticmethod
    def UpdateCurrentSession():
        session = DBEngine._commonsession
        # Log.Write("UpdateCurrentSession", session)
        try:
            # session.flush()
            session.commit()
            session.expunge_all()
        except Exception, e:
            Log.Write(e)
            Log.Write(traceback.format_exc())
            session.close()
            # DBEngine._commonsession = DBEngine._sessionmaker()

    @staticmethod
    def DelGreenletSession(glet):
        session = DBEngine._commonsession
        try:
            session.commit()
            session.expunge_all()
        except Exception, e:
            Log.Write(e)
            Log.Write(traceback.format_exc())
        session.close()
        DBEngine._commonsession = DBEngine._sessionmaker()

    def _saveupdaterecord(target):
        with session_scope2() as session:
            # Log.Write("DBEngine.add", session, target)
            session.add(target)
            return target

    def _saveupdaterecord2(target):
        with session_scope() as session:
            # Log.Write("DBEngine.add", session, target)
            session.add(target)
            return target

    Add = staticmethod(_saveupdaterecord)
    Update = staticmethod(_saveupdaterecord2)

    # @staticmethod
    # def Add(target):
    #     with session_New() as session:
    #         session.add(target)
    #         return target

    @staticmethod
    def Delete(target):
        with session_scope() as session:
            session.delete(target)
            return target

    @staticmethod
    def BindVar(target):
        session = DBEngine.NewSession()
        session.add(target)

    @staticmethod
    def Expunge(target):
        with session_scope() as session:
            session.expunge(target)


def MakeRenameSQL(t1,t2):
    return "alter table %s rename to %s;" % (t1, t2)


def MakeTruncateSQL(t):
    return "truncate %s;" % (t,)


def ExcuteSQL(sql):
    with session_New() as session:
        session.execute(sql)