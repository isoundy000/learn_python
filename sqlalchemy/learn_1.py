# -*- encoding: utf-8 -*-
'''
Created on 2018年4月10日

@author: houguangdong
'''
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import func
# 创建实例，并连接dong库
engine = create_engine("mysql+mysqldb://root:donga123@localhost:3306/dong", encoding='utf-8', echo=False)
# echo=True 显示信息
Base = declarative_base()   # 生成orm基累


class User(Base):

    __tablename__ = 'new_user'  # 表名
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    password = Column(String(64))

    # 不过刚才显示的内存对象对址没办法分清返回的是什么数据的，除非打印具体字段看一下，如果想让它变的可读，只需在定义表的类下面加上这样的代码
    def __repr__(self):
        return "<User(name='%s, password='%s)>" % (self.name, self.password)

# Base.metadata.create_all(engine)    # 创建表结构 （这里是父类调子类)


# 第二种创建表的方式
from sqlalchemy import Table, MetaData, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

# metadata = MetaData()

# tmp_user = Table(
#     'tmp_user', metadata,
#     Column('id', Integer, primary_key=True),
#     Column('name', String(50)),
#     Column('fullname', String(50)),
#     Column("password", String(12))
# )


class Tmp_User(object):

    def __index__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password


# mapper(Tmp_User, tmp_user)  # 类Tmp_User和tmp_user关联起来 如果数据库里有，就不会创建了。
# 插入一条数据
# 创建与数据库的会话session class ,注意,这里返回给session的是个class,不是实例
Session_class = sessionmaker(bind=engine)   # 实例和engine绑定
Session = Session_class()                   # 生成session实例，相当于游标
user_obj = User(name="fgf", password="123456")  # 生成你要创建的数据对象
# Session.add(user_obj)   # 把要创建的数据对象添加到这个session里， 一会统一创建
# Session.commit()        # 现此才统一提交，创建数据

# 3.1、查询
my_user = Session.query(User).filter_by(name="fgf").first()
# my_user = Session.query(User).filter_by().all()  # 查询所有
print my_user
all_user = Session.query(User.name, User.id).all()
for i in all_user:
    print i
# 3.2、多条件查询filter_by与filter
my_user1 = Session.query(User).filter(User.id > 2).all()
my_user2 = Session.query(User).filter_by(id=27).all()   # filter_by相等用‘=’
my_user3 = Session.query(User).filter(User.id == 27).all()    # filter相等用‘==’
print my_user2, my_user3
objs = Session.query(User).filter(User.id > 26).filter(User.id < 28).all()
print objs
# 4、修改
# my_user.name = "fenggf"     # 查询出来之后直接赋值修改
# my_user.password = "123qwe"
# Session.commit()
# 5、回滚
# my_user = Session.query(User).filter_by(id=1).first()
# my_user.name = "Jack"
fake_user = User(name="Rain", password='12345')
Session.add(fake_user)
print Session.query(User).filter(User.name.in_(["Jack",  "rain"])).all(), '111'    # 这时看session里有你刚添加和修改的数据
Session.rollback()      # 此时你rollback一下
print(Session.query(User).filter(User.name.in_(['Jack', 'rain']))).all(), '222'    # 再查就发现刚才添加的数据没有了。
# Session.commit()
# 6、统计和分组 统计 count 分组 group_by
print Session.query(User).filter(User.name.like("f%")).count()    # mysql不区分大小写
print Session.query(User.name, func.count(User.name)).group_by(User.name).all()
# 7.1、外键关联 准备工作：先创建一个表，再插入数据
