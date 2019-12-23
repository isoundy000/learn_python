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
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import aliased
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import text
from sqlalchemy import func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy import connectors


# 创建实例， 并连接dong库
engine = create_engine('mysql+mysqldb://root:donga123@localhost:3306/dong')
Session = sessionmaker(bind=engine)

# echo=True显示信息
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'  # 表名
    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    fullname = Column(String(32))
    password = Column(String(64))
    # addresses = relationship("Address", order_by="Address.id", backref="user")


class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    email_address = Column(String(64), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", backref=backref('addresses', order_by=id))
    def __repr__(self):
        return "<Address(email_address='%s')>" % self.email_address

# 构造类和外键简单，就不过多赘述。主要说明以下relationship()函数：这个函数告诉ORM，Address类应该和User类连接起来，通过使用addresses.user。relationship()使用外键明确这两张表的关系。决定Adderess.user属性是多对一的。relationship()的子函数backref()提供表达反向关系的细节：relationship()对象的集合被User.address引用。多对一的反向关系总是一对多。更多的细节参考Basic RelRational Patterns。
# 这两个互补关系：Address.user和User.addresses被称为双向关系。这是SQLAlchemy ORM的一个非常关键的功能。更多关系backref的细节参见Linking Relationships with Backref。
# 假设声明的方法已经开始使用，relationship()中和其他类关联的参数可以通过strings指定。在上文的User类中，一旦所有映射成功，为了产生实际的参数，这些字符串会被当做Python的表达式。下面是一个在User类中创建双向联系的例子：
# 一些知识：
# 在大多数的外键约束（尽管不是所有的）关系数据库只能链接到一个主键列，或具有唯一约束的列。
# 外键约束如果是指向多个列的主键，并且它本身也具有多列，这种被称为“复合外键”。
# 外键列可以自动更新自己来相应它所引用的行或者列。这被称为级联，是一种建立在关系数据库的功能。
# 外键可以参考自己的表格。这种被称为“自引”外键。
# 我们需要在数据库中创建一个addresses表，所以我们会创建另一个元数据，这将会跳过已经创建的表。

ed_user = User(name='ed', fullname='Ed Jones', password='edspassword')

user_alias = aliased(User, name='user_alias')


def main():
    Base.metadata.create_all(engine) #创建表结构 （这里是父类调子类）
    session = Session()
    # 7.添加新对象（简略）
    # session.add(ed_user)
    # 通过commit()可以提交所有剩余的更改到数据库
    # session.commit()
    # 8.回滚
    # session.rollback()
    # 9.查询
    # 通过Session的query()方法创建一个查询对象。这个函数的参数数量是可变的，参数可以是任何类或者是类的描述的集合。下面是一个迭代输出User类的例子：
    for instance in session.query(User).order_by(User.id):
        print(instance.id, instance.name, instance.fullname, instance.password)
    # Query也支持ORM描述作为参数。任何时候，多个类的实体或者是基于列的实体表达都可以作为query()
    # 函数的参数，返回类型是元组：
    for name, fullname in session.query(User.name, User.fullname):
        print(name, fullname)
    # Query返回的元组被命名为KeyedTuple类的实例元组。并且可以把它当成一个普通的Python数据类操作。元组的名字就相当于属性的属性名，类的类名一样。
    for row in session.query(User, User.name).all():
        print(row.User, row.name)
    # label()不知道怎么解释，看下例子就明白了。相当于row.name
    for row in session.query(User.name.label('name_label')).all():
        print(row.name_label)
    # aliased()我的理解是类的别名，如果有多个实体都要查询一个类，可以用aliased()
    for row in session.query(user_alias, user_alias.name).all():
        print(row.user_alias)
    # Query的基本操作包括LIMIT和OFFSET，使用Python数组切片和ORDERBY结合可以让操作变得很方便。
    for u in session.query(User).order_by(User.id)[1:3]:
        print(u.name, u.password)
    # 9.1使用关键字变量过滤查询结果，filter和filter_by都适用。【2】使用很简单，下面列出几个常用的操作：
    for u in session.query(User).filter(User.name == 'ghou'): # equals
        print(u.name, u.fullname, "====")
    for u in session.query(User).filter(User.name != 'ed'): # not equals
        print(u.name)
    for u in session.query(User).filter(User.name.like('%ghou%')): # LIKE
        print(u.fullname)
    for u in session.query(User).filter(User.name.in_(['ghou','wendy', 'jack'])): # IN
        print(u.name)
    for u in session.query(User).filter(User.name.in_(session.query(User.name).filter(User.name.like('%ed%')))): # IN
        print(u.fullname)
    for u in session.query(User).filter(~User.name.in_(['ed','wendy', 'jack'])): # not IN
        print(u.name)
    for u in session.query(User).filter(User.name == None): # is None
        print(u.fullname)
    for u in session.query(User).filter(User.name != None): # not None
        print(u.name, "-----")
    for u in session.query(User).filter(and_(User.name =='ed', User.fullname =='Ed Jones')): # and
        print(u.fullname)
    for u in session.query(User).filter(User.name == 'ed', User.fullname =='Ed Jones'): # and
        print(u.name)
    for u in session.query(User).filter(User.name == 'ed').filter(User.fullname == 'Ed Jones'): # and
        print(u.fullname)
    for i in session.query(User).filter(or_(User.name =='ed', User.name =='ghou')): # or
        print(i.fullname)
    # for i in session.query(User).filter(User.name.match('ed')): # match
    #     print i.fullname
    # 9.2.返回列表和数量（标量？）
    # all()返回一个列表：可以进行Python列表的操作。
    query = session.query(User).filter(User.name.like("%ed")).order_by(User.id).all()
    for i in query:
        print(i.fullname, "++++")
    # first()适用于限制一个情况，返回查询到的第一个结果作为标量？：好像只能作为属性，类
    query1 = session.query(User).filter(User.name.like("%ed")).order_by(User.id).first()
    print('-----', query1.fullname)
    # one()完全获取所有行，并且如果查询到的不只有一个对象或是有复合行，就会抛出异常。
    try:
        u1 = session.query(User).one()
        print(u1.name)
    except MultipleResultsFound as e:
        print(e)
    # 如果一行也没有：
    try:
        user = session.query(User).filter(User.id == 99).one()
    except NoResultFound as e:
        print(e)
    # one()方法对于想要解决“no items found”和“multiple items found”是不同的系统是极好的。（这句有语病啊）例如web服务返回，本来是在no
    # results found情况下返回”404“的，结果在多个results found情况下也会跑出一个应用异常。

    # scalar()作为one()方法的依据，并且在one()成功基础上返回行的第一列。
    query = session.query(User.id).filter(User.name == 'ghou')
    print(query.scalar())
    # 9.3.使用字符串SQL
    # 字符串能使Query更加灵活，通过text()构造指定字符串的使用，这种方法可以用在很多方法中，像filter()和order_by()。
    for k in session.query(User).filter(text("id<5")).order_by(text("id")).all():
        print(k.name, k.fullname, 'kkkk')
    # 绑定参数可以指定字符串，用params()方法指定数值。
    tmp = session.query(User).filter(text("id<:value and name=:name")).params(value=224, name='ghou').order_by(User.id).one()
    print(tmp.fullname, tmp.name, 'jjjj')
    # 如果要用一个完整的SQL语句，可以使用from_statement()。
    for j in session.query(User).from_statement(text("SELECT * FROM user where name=:name")).params(name='ed').all():
        print(j.name, j.fullname, 'jjjjjjjj')
    # 也可以用from_statement()获取完整的”raw”，用字符名确定希望被查询的特定列:
    for h in session.query("id", "name", "thenumber12").from_statement(text("SELECT id, name, fullname as thenumber12 FROM user where name=:name")).params(name='ed').all():
        print(h.name, h.thenumber12, 'hhhh')
    # 9.4计数
    # count()用来统计查询结果的数量。
    print(session.query(User).filter(User.name.like('%ed')).count())
    # func.count()方法比count()更高级一点【3】
    for k1 in session.query(func.count(User.name), User.name).group_by(User.name).all():
        print(k1)
    # 为了实现简单计数SELECT count(*) FROM table，可以这么写：
    print(session.query(func.count('*')).select_from(User).scalar())
    # 如果我们明确表达计数是根据User表的主键的话，可以省略select_from(User):
    print(session.query(func.count(User.id)).scalar())
    # 10.建立联系（外键）
    # 是时候考虑怎样映射和查询一个和Users表关联的第二张表了。假设我们系统的用户可以存储任意数量的email地址。我们需要定义一个新表Address与User相关联。
    # 11.操作主外键关联的对象
    # 现在我们已经在User类中创建了一个空的addresser集合，可变集合类型，例如set和dict，都可以用，但是默认的集合类型是list。
    jack = User(name='jack', fullname='Jack Bean', password='gjffdd')
    print(jack.addresses)
    # 现在可以直接在User对象中添加Address对象。只需要指定一个完整的列表：
    jack.addresses = [Address(email_address='jack@google.com'), Address(email_address='j25@yahoo.com')]
    print(jack.addresses[1])


if __name__ == '__main__':
    main()