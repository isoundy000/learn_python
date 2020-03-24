#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'


# ### another way (but again *not the only way*) to do it ###
#
# from contextlib import contextmanager
#
# @contextmanager
# def session_scope():
#     """Provide a transactional scope around a series of operations."""
#     session = Session()
#     try:
#         yield session
#         session.commit()
#     except:
#         session.rollback()
#         raise
#     finally:
#         session.close()
#
#
# def run_my_program():
#     with session_scope() as session:
#         ThingOne().go(session)
#         ThingTwo().go(session)
#
#
#
# ### this is a **better** (but not the only) way to do it ###
#
# class ThingOne(object):
#     def go(self, session):
#         session.query(FooBar).update({"x": 5})
#
# class ThingTwo(object):
#     def go(self, session):
#         session.query(Widget).update({"q": 18})
#
# def run_my_program():
#     session = Session()
#     try:
#         ThingOne().go(session)
#         ThingTwo().go(session)
#
#         session.commit()
#     except:
#         session.rollback()
#         raise
#     finally:
#         session.close()