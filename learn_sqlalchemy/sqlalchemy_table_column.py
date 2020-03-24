#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# SQLAlchemy Table（表）类方式 - Table类和Column类
# Table
# 构造方法
# 1 Table(name, metadata[, *column_list][, ** kwargs])
# 参数说明:
#     name            表名
#     metadata        元数据对象
#     column_list     是列(Column或其他继承自SchemaItem的对象)列表
#     kwargs主要内容：
#         schema: (None)表的模式（一般默认是数据库名, 无需特别指定;Oracle中是owner, 当一个数据库由多个用户管理时，用户的默认数据库不是要连接的数据库时，需要指定此项）
#         autoload: (False) 是否自动加载
#         autoload_replace: (True)是否自动用元数据中加载的列替换column_list中已经存在了的同名列
#             为True时自动将column_list中已经存在了的列替换为从元数据中加载的同名列
#             为False时会忽略元数据有，且column_list中已经存在了的列
#         autoload_with: 自动加载的引擎(Engine)或连接(Connection)对象
#             为None时
#                 autoload为True时, 会从传递的metadata中寻找引擎或连接对象
#             不为None时
#                 当autoload不为True时, autoload会自动被修改为True
#         comment: 注释
#         extend_existing: (False)当表已经存在于元数据中时，如果元数据中存在与column_list中的列同名的列，column_list中同名的列会替换掉元数据中已经有的列
#         keep_existing: (False)当表已经存在于元数据中时，如果元数据中存在与column_list中的列同名的列，column_list中同名的列会被忽略
#         include_columns：(None)从元数据中只需加载的表的列名列表
#         mustexist: (False)表名是否一定需要存在于元数据中（不存在时引发异常）
#
# 常用SchemaItem子类：
#     PrimaryKeyConstraint
#     ForeignKeyConstraint
#
# 注意，在使用不同版本的SQLAlchemy时，以上参数中：
#     老版本中可能部分参数还没有
#     新版本中可能废弃了部分参数
#     keep_existing与extend_existing互相排斥，不能同时传递为True
#     keep_existing与extend_existing适用于新建表对象；如果要创建新的表，表明已经存在于meta.tables中时，需要指明任意一个参数，不然会报错。
#     useexisting已被废弃, 新版本使用extend_existing
#
# 
# Column的构造方法
#     Column([name, ]type_[, ** kwargs])
#
# 参数说明：
#     name 字段名
#     type_ 字段数据类型，这里的数据类型包括：
#     SQLAlchemy中常用数据类型:
#         整数: SmallInteger、Integer、BigInteger等
#         浮点数: Float、Numeric等
#         文本字符串: String、Text、Unicode、UnicodeText、CHAR、VARCHAR等
#         二进制字符串: LargeBinary、BINARY、VARBINARY等
#         日期时间: Date、DateTime、TIMESTAMP等
#     Constraint: 约束
#     ForeignKey: 外键
#     ColumnDefault: 列默认值
#     kwargs主要内容：
#         autoincrement: (False)是否是主键
#         default: (None)默认值
#         index: (None)索引
#         nullable: (True)是否可以为空(NULL)
#         primary_key: (False)是否是主键
#         server_default: (None)服务端(数据库中的函数)默认值
#         unique: (False)是否唯一
#         comment: (None)列注释