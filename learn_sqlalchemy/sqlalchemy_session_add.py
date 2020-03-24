#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# 添加新项目或现有项目
# add()用于在会话中放置实例。对于瞬态(即全新的)实例，这将在下一次刷新时对这些实例执行插入操作。对于持久的实例(即由此会话加载的实例)，
# 它们已经存在，不需要添加。分离的实例(即从会话中删除的实例)可以使用以下方法与会话重新关联:
#
# user1 = User(name='user1')
# user2 = User(name='user2')
# session.add(user1)
# session.add(user2)
#
# session.commit()     # write changes to the database
#
# 要立即向会话添加项目列表，请使用add_all():
# session.add_all([item1, item2, item3])