# -*- encoding: utf-8 -*-
'''
Created on 2018年4月10日

@author: houguangdong
'''
# 1.版本检查
import sqlalchemy
# sqlalchemy.__version__
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, MetaData, Column, Integer, String, Enum, DATE, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker, relationship
from sqlalchemy import func, or_, not_
# 创建实例，并连接test库
engine = create_engine("mysql+mysqldb://sanguo_bg:sanguo_passwd@localhost:3306/ghou",
                                    encoding='utf-8', echo=False)

metadata = MetaData()
Base = declarative_base()  # 生成orm基类

user = Table(
    'user', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(50)),
    Column('password', String(12))
)


class User(object):

    def __init__(self, name, id, password):
        self.id = id
        self.name = name
        self.password = password

    def __repr__(self):
        return "[%s name: %s]" % (self.id, self.name)

# the table metadata is created separately with the Table construct, then associated with the User class via the mapper() function
mapper(User, user)

# 创建与数据库的会话session class ,注意,这里返回给session的是个class,不是实例
Session_class = sessionmaker(bind=engine)  # 实例和engine绑定
Session = Session_class()  # 生成session实例，相当于游标

# Session.execute('create database abc')
# print Session.execute('show databases').fetchall()
# Session.execute('use abc')
# print Session.execute('select * from user where id = 1').first()
# print Session.execute('select * from user where id = :id', {'id': 1}).first()
# def init_db():
#     Base.metadata.create_all(engine)  # 创建表结构
# def drop_db():
#     Base.metadata.drop_all(engine)
# BaseModel.metadata.create_all(engine) 会找到 BaseModel 的所有子类，并在数据库中建立这些表；drop_all() 则是删除这些表。


user_obj = User(id=27, name="fgf", password="123456")  # 生成你要创建的数据对象
# Session.add(user_obj)   # 把要创建的数据对象添加到这个session里， 一会统一创建
# user_obj = Session.query(User).filter(User.id ==27).first()
# Session.delete(user_obj)
# Session.flush()


# 删除 del
# 7.1、外键关联
# 准备工作：先创建一个表，再插入数据

class Student(Base):

    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, autoincrement=True)
    stu_id = Column(Integer)
    age = Column(Integer)
    gender = Column(Enum('M', 'F'), nullable=False)

    def __repr__(self):
        return "[%s stu_id:%s sex:%s]" % (self.stu_id, self.age, self.gender)


# Base.metadata.create_all(engine)     # 创建表结构 （这里是父类调子类）
# stu_obj = Student(stu_id=27, age=22, gender="M")
# Session.add(stu_obj)

res = Session.query(User, Student).filter(User.id == Student.stu_id).all()
print res


class Stu2(Base):

    __tablename__ = "stu2"
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    register_date = Column(DATE, nullable=False)

    def __repr__(self):
        return "<%s name:%s>" % (self.id, self.name)


class StudyRecord(Base):

    __tablename__ = 'study_record'
    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False)
    status = Column(String(32), nullable=False)
    stu_id = Column(Integer, ForeignKey("stu2.id"))     # ------外键关联------
    # 这个nb, 允许你在Stu2表里通过backref字段反向查询所有它在StudyRecord表里的关联项数据
    stu2 = relationship("Stu2", backref="my_study_record")     # 添加关系，反查（在内存里）
    # 大致原理应该就是sqlalchemy在运行时对Stu2对象动态的设置了一个指向所属StudyRecord对象的属性，这样就能在实际开发中使逻辑关系更加清晰，代码更加简洁了。
    # 简单地说就是:  backref用于在关系另一端的类中快捷地创建一个指向当前类对象的属性, 而当需要对那个属性指定参数时使用db.backref()

    def __repr__(self):
        return "<%s day:%s status:%s>" % (self.stu2.name, self.day, self.status)


Base.metadata.create_all(engine)     # 创建表结构 （这里是父类调子类）

s1 = Stu2(name="A", register_date="2014-05-21")
s2 = Stu2(name="J", register_date="2014-03-21")
s3 = Stu2(name="R", register_date="2014-02-21")
s4 = Stu2(name="E", register_date="2013-01-21")

study_obj1 = StudyRecord(day=1, status="YES", stu_id=1)
study_obj2 = StudyRecord(day=2, status="NO", stu_id=1)
study_obj3 = StudyRecord(day=3, status="YES", stu_id=1)
study_obj4 = StudyRecord(day=1, status="YES", stu_id=2)

Session.add_all([s1, study_obj1, s2, study_obj2, s3, s4, study_obj3, study_obj4])   # 创建

stu_obj = Session.query(Stu2).filter(Stu2.name == 'a').first()  # 查询
# 在stu2表, 查到StudyRecord表的记录
print stu_obj
print stu_obj.my_study_record   # 查询A一共上了几节课
# 可以查看创建命令：
# show create table study_record;

# 7.2、多外键关联
# 多外键关联，并且关联同一个表。
# 下表中，Customer表有2个字段都关联了Address表
class Customer(Base):

    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    # 账单地址和邮寄地址 都关联同一地址表
    billing_address_id = Column(Integer, ForeignKey("address.id"))
    shipping_address_id = Column(Integer, ForeignKey("address.id"))

    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])


class Address(Base):

    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    street = Column(String(64))
    city = Column(String(64))
    state = Column(String(64))

    def __repr__(self):
        return self.street

Base.metadata.create_all(engine)  # 创建表结构 （这里是父类调子类）

# 正常写的时候，表结构单独写一个模块。添加数据
addr1 = Address(street="Tiantongyuan", city="ChangPing", state="BJ")
addr2 = Address(street="Wudaokou", city="Haidian", state="BJ")
addr3 = Address(street="Yanjiao", city="LangFang", state="HB")
# Session.add_all([addr1, addr3, addr2])
c1 = Customer(name="Fgf", billing_address=addr1, shipping_address=addr2)
c2 = Customer(name="Jack", billing_address=addr3, shipping_address=addr3)
# Session.add_all([c1, c2])

obj = Session.query(Customer).filter(Customer.name == 'Fgf').first()
print obj.name, obj.billing_address, obj.shipping_address

# 7.3 多对多关系
# 现在来设计一个能描述“图书”与“作者”的关系的表结构，需求是
# 一本书可以有好几个作者一起出版
# 一个作者可以写好几本书
# 此时你会发现，用之前学的外键好像没办法实现上面的需求了
# 那怎么办呢？ 此时，我们可以再搞出一张中间表，就可以了
# 这样就相当于通过book_m2m_author表完成了book表和author表之前的多对多关联
# 双向一对多，就是多对多。
# 用orm如何表示呢？
# 第三张表 自己创建。不需要手动管理，orm自动维护
book_m2m_author = Table(
    'book_m2m_author', Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id')),
    Column('author_id', Integer, ForeignKey('authors.id')),
)


class Book(Base):

    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    pub_date = Column(DATE)
    # book表不知道第三张表，所以关联一下第三张表
    authors = relationship('Author', secondary=book_m2m_author, backref='books')

    def __repr__(self):
        return self.name


class Author(Base):

    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String(32))

    def __repr__(self):
        return self.name


# 创建书
b1 = Book(name="learn python with Alex", pub_date="2014-05-2")
b2 = Book(name="learn Zhangbility with Alex", pub_date="2015-05-2")
b3 = Book(name="Learn hook up girls with Alex", pub_date="2016-05-2")
# 创建作者
a1 = Author(name="Alex")
a2 = Author(name="Jack")
a3 = Author(name="Rain")
a4 = Author(name="侯广东")
# 关联关系
b1.authors = [a1, a3]
b3.authors = [a1, a2, a3]
Session.add_all([b1, b2, b3, a1, a2, a3, a4])
Base.metadata.create_all(engine)  # 创建表结构
# 重要是查询
author_obj = Session.query(Author).filter(Author.name == 'alex').first()
print author_obj.books[0:]
book_obj = Session.query(Book).filter(Book.id == 3).first()
print book_obj.authors, book_obj.name, book_obj.pub_date

# 多对多删除
# 删除数据时不用管boo_m2m_authors, sqlalchemy会自动帮你把对应的数据删除
# 通过书删除作者
author_obj = Session.query(Author).filter_by(name='rain').first()
book_obj = Session.query(Book).filter_by(name='Learn hook up girls with Alex').first()
print book_obj.authors.remove(author_obj)   # 从一本书里删除一个作者

# 直接删除作者
# 删除作者时，会把这个作者跟所有书的关联关系数据也自动删除
author_obj = Session.query(Author).filter_by(name='Alex').first()
sql_tmp = Session.query(Author)
print sql_tmp, '111111111'
print sql_tmp.statement, '22222222'  # 显示SQL 语句
print sql_tmp.all()   # 返回的是一个类似列表的对象
print sql_tmp.first().name  # 记录不存在时，first() 会返回 None
# print sql_tmp.one().name    # 不存在，或有多行记录时会抛出异常
print sql_tmp.filter(Author.id == 2).first().name
print sql_tmp.get(2).name   # 以主键获取，等效于上句
print sql_tmp.filter('id = 2').first().name, '3333333333'     # 支持字符串

query2 = Session.query(Author.name)
print query2.all()  # 每行是个元组
print query2.limit(1).all()     # 最多返回 1 条记录
print query2.offset(1).all()    # 从第 2 条记录开始返回
print query2.order_by(Author.name).all()
print query2.order_by('name').all()
print query2.order_by(Author.name.desc()).all()
print query2.order_by('name desc').all()
print Session.query(Author.id).order_by(Author.name.desc(), Author.id).all(), '44444444'
print query2.filter(Author.id == 1).scalar()    # 如果有记录，返回第一条记录的第一个元素
print Session.query('id').select_from(Author).filter('id = 1').scalar()
print query2.filter(Author.id > 1, Author.name == 'a').scalar() # and
query3 = query2.filter(Author.id > 1)   # 多次拼接的 filter 也是 and
query3 = query3.filter(Author.name == 'a')
print query3.scalar()
print query2.filter(or_(Author.id == 1, Author.id == 2)).all()  # or
print query2.filter(Author.id.in_((1, 2))).all(), '55555'    # in

query4 = Session.query(Author.id)
print query4.filter(Author.name == None).scalar()
print query4.filter('name is null').scalar()
print query4.filter(not_(Author.name == None)).all() # not
print query4.filter(Author.name != None).all()
print query4.count(), '666666'

print Session.query(func.count('*')).select_from(Author).scalar()
print Session.query(func.count('1')).select_from(Author).scalar()
print Session.query(func.count(Author.id)).scalar()
print Session.query(func.count('*')).filter(Author.id > 0).scalar() # filter() 中包含 User，因此不需要指定表
print Session.query(func.count('*')).filter(Author.name == 'a').limit(1).scalar() == 1  # 可以用 limit() 限制 count() 的返回数
print Session.query(func.sum(Author.id)).scalar()
print Session.query(func.now()).scalar()    # func 后可以跟任意函数名，只要该数据库支持
print Session.query(func.current_timestamp()).scalar()
print Session.query(func.md5(Author.name)).filter(Author.id == 2).scalar(), '777777'

sql_tmp.filter(Author.id == 2).update({Author.name: 'c'})
user1 = sql_tmp.get(3)
print user1.name
user1.name = 'd'
Session.flush()     # 写数据库，但并不提交
print sql_tmp.get(3).name,      '8888888'

Session.delete(author_obj)
Session.flush()
print sql_tmp.get(3)
Session.rollback()
print sql_tmp.get(3).name
sql_tmp.filter(Author.id == 3).delete()
Session.commit()
print sql_tmp.get(3)

print author_obj.name, author_obj.books
# Session.delete(author_obj)
Base.metadata.create_all(engine)  # 创建表结构
Session.commit()    # 现此才统一提交，创建数据

# 8、中文问题 先查看数据库的字符集
# show create database ghou;
# 修改数据库的字符集（如果修改字符集，添加仍不显示中文，可能就需要创建是指定尝试一下了。）
# alter database ghou character set utf8;
# 创建数据库指定数据库的字符集
# create database ghou character set utf8;
# sqlalchemy 连接指定
# engine = create_engine("mysql+pymysql://root:123456@localhost/test?charset=utf8",)