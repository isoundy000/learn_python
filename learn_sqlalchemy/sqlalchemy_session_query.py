#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# # query from a class
# session.query(User).filter_by(name='ed').all()
#
# # query with multiple classes, returns tuples
# session.query(User, Address).join('addresses').filter_by(name='ed').all()
#
# # query using orm-enabled descriptors
# session.query(User.name, User.fullname).all()
#
# # query from a mapper
# user_mapper = class_mapper(User)
# session.query(user_mapper)


