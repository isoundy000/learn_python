#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# Flushing
# 当会话与其默认配置一起使用时，刷新步骤几乎总是透明地完成的。具体来说，刷新发生在发出单个查询之前，以及提交事务之前的commit()调用中。当使用begin_嵌套()方法时，它也发生在发出保存点之前。
# 不管自动刷新设置如何，刷新总是可以通过发出flush()来强制执行:
# session.flush()
# 不管自动刷新设置如何，总是可以通过发出flush()来强制刷新:通过使用autoflush=False构造sessionmaker，可以禁用行为的“查询上刷新”方面:
# Session = sessionmaker(autoflush=False)
# 另外，通过随时设置自动刷新标志，可以暂时禁用自动刷新:
# mysession = Session()
# mysession.autoflush = False
# 刷新过程总是在事务内部发生，即使会话已经配置了autocommit=True，这个设置会禁用会话的持久事务状态。如果不存在事务，flush()创建自己的事务并提交。刷新期间的任何故障都将导致出现任何事务的回滚。如果会话不是在autocommit=True模式下，那么在刷新失败后需要显式调用rollback()，即使底层事务已经回滚了——这样就可以始终保持所谓的“子事务”的整体嵌套模式。