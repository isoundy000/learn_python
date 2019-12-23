#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/11/25 11:44
# @version: 0.0.1
# @Author: houguangdong
# @File: test_alchimia.py
# @Software: PyCharm

from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String
)

from sqlalchemy.schema import CreateTable

from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import react

from learn_twist.dbentrust.alchimia import wrap_engine


@inlineCallbacks
def main(reactor):
    engine = wrap_engine(reactor, create_engine(
        "mysql+pymysql://root:123456@127.0.0.1:3306/dong?charset=utf8mb4&binary_prefix=true",
        # encoding='utf8mb4',
        pool_recycle=3600,
        pool_size=100,
        pool_pre_ping=True,
        # binary_prefix=True,
        echo=True,
    ))

    metadata = MetaData(engine)
    users = Table("users_test", metadata,
                  Column("id", Integer(), primary_key=True),
                  Column("name", String(32))
                  )
    # Create the table
    # yield engine.execute(CreateTable(users))

    # Insert some users
    yield engine.execute(users.insert().values(name="Jeremy Goodwin"))
    yield engine.execute(users.insert().values(name="Natalie Hurley"))
    yield engine.execute(users.insert().values(name="Dan Rydell"))
    yield engine.execute(users.insert().values(name="Casey McCall"))
    yield engine.execute(users.insert().values(name="Dana Whitaker"))

    result = yield engine.execute(users.select(users.c.name.startswith("D")))
    d_users = yield result.fetchall()
    # Print out the users
    for user in d_users:
        print("Username: %s" % user[users.c.name])
    # Queries that return results should be explicitly closed to
    # release the connection

    # yield engine.execute(users.delete())
    result.close()


if __name__ == "__main__":
    create_engine("mysql+pymysql://root:123456@127.0.0.1:3306/dong", echo=True)
    react(main, [])