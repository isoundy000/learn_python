#!/usr/bin/env python
#coding: utf-8

# 创建数据库
# create database osdbadb;
# 修改数据库
# alter database testdb01 CONNECTION LIMIT 10;
# 改变数据库testdb01的名称为mydb01;
# alter database testdb01 rename to mydb01;
# 关闭数据库testdb01上的默认索引扫描
# alter database testdb01 set enable_indexscan TO off;

# 删除数据库
# drop database mytestdb01;
# drop database if exists mytestdb01;
# begin:
# alter database testdb01 rename to mydb01;
# rollback;

# 模式
# 创建、查看、删除和修改模式
# 创建一个名为"osdba"的模式
# create schema osdba;
# 查看有那些模式
# \dn

# 删除一个模式
# drop schema osdba;
# 下面的命令为用户"osdba"创建模式, 名字也定为"osdba";
# create schema authorization osdba;

# 在创建一个模式的同时, 还可以在这个模式下创建一些表的视图
# create schema osdba
#     create table t1 (id int, title text)
#     create table t2 (id int, content text)
#     create view v1 as
#         select a.id, a.title, b.content from t1 a, t2 b where a.id = b.id;

# \d 查看
# 在模式中可以修改名称和属主
# ALTER SCHEMA name RENAME TO newname
# ALTER SCHEMA name OWNER TO newowner
# 改名称的示例如下
# alter schema osdba rename to osdbaold;
# \dn 查看
# 改属主的示例如下
# alter schema osdbaold owner to web;

# 公共模式
# 要创建或者访问模式中的对象, 需要先写一个受修饰的名字, 这个名字包含模式名及表名, 它们之间用一个"点"分开
# schema_name.table_name

# 模式的搜索路径
# SHOW search_path;
# 模式的权限
# 默认的情况, 用户无法访问模式中不属于它们的对象。若要访问, 模式的所有者必须在模式上赋予它们"USAGE"权限。
# 默认在public模式上都有"CREATE"和"USAGE"权限, 允许所有连接到指定数据库上的用户在这里创建对象。可以撤销这个权限。
# REVOKE create on schema public from PUBLIC;
# 第一public是模式的名称, 第二个"PUBLIC"的意思是"所有用户"。在第一句里他是个标识符, 而第二句里是个关键字。

# 模式相当于mysql数据库

# 表
# create table test01(id int primary key, note varchar(20));
# 复合主键、约束子句的语法, 主键的约束子句语法为:
# CONSTRAINT constraint_name PRIMARY KEY (col1_name, col2_name);
# create table test02(id int, id2 int, note varchar(20), CONSTRAINT pk_test02 primary key(id1, id2));
# 唯一键约束
# CONSTRAINT constraint_name UNIQUE(col1_name, col2_name, ...);
# create table test03 (id1 int, id2 int, id3 int, note varchar(20), CONSTRAINT pk_test03 primary key(id1, id2), CONSTRAINT uk_test03_id3 UNIQUE(id3));

# check约束 检查约束
# CONSTRAINT constraint_name CHECK (expression)
# create table child(name varchar(20), age int, note text, CONSTRAINT ck_child_age CHECK(age < 18));

# 除了上面的建表方式以外, 还可以用其他表为模板创建新表
# CREATE TABLE baby (LIKE child);   # 没有把源表列上的约束复制过来
# \d baby   查看
# \d child  查看

# 如果想完全复制源表列上的约束和其他信息, 则需要加"INCLUDING"
# create table baby2 (like child including all);
# \d baby2
# 当然也可以使用create table ... as 来创建表

# 修改TOAST策略
# PLAIN: 避免压缩或线外存储
# EXTENDED: 允许压缩或线外存储
# EXTERNAL: 允许行外存储、但是不许压缩
# MAIN: 允许压缩, 但不允许行外存储。
# create table blog(id int, title text, content text);
# alter table blog alter content set storage EXTERNAL;

# 临时表(会话级别|事务级别)
# create TEMPORARY table tmp_t1 (id int primary key, note text);
# \d 本session可以看到这张表
# 其他session可以通过 \d pg_tmp_xxx.tmp_t1查看

# 事务级的临时表
# create TEMPORARY table tmp_t2 (id int primary key, note text) on commit delete rows;
# begin:
# insert into tmp_t2 values(1, 'aaa');
# insert into tmp_t2 values(2, 'bbb');
# select * from tmp_t2;
# end;

# select * from tmp_t2;
# 实际上on commit子句有以下三种形式
# on commit preserve rows: 若不带on commit子句, 默认情况下，数据一值存在于整个会话周期中
# on commit delete rows: 数据存在于事务周期中，事务一提交，数据就消失了
# on commit drop: 数据存在于事务周期中，事务一提交，数据就消失了

# 下面的sql等价
# create TEMPORARY table tmp_t1(id int primary key, note text);
# create TEMP table tmp_t1(id int primary key, note text);
# create GLOBAL TEMPORARY table tmp_t1(id int primary key, note text);
# create LOCAL TEMPORARY table tmp_t1(id int primary key, note text);

# 默认值
# create table student(no int, name varchar(20), age int default 15);
# insert into student(no, name) values(1, '张三');
# insert into student(no, name) values(2, '李四');
# update student set age = DEFAULT where no = 2;

# timestamp字段默认值now()
# create table blog(id int, title text, created_date timestamp default now());
# \d blog;
# insert into blog values(1, 'PostgreSQL创建临时表');
# select * from blog;

# 约束
# 检查约束
# create table person(name varchar(40), age int CHECK (age >= 0 and age <= 150), sex boolean);
# 可以给约束起名字
# create table person(name varchar(40), age int CONSTRAINT check_age CHECK (age >= 0 and age <= 150), sex boolean);
# create table books(book_no integer, name text, price numeric CHECK (price > 0), discounted_price numeric CHECK (discounted_price > 0), CHECK (price > discounted_price));
# create table books(book_no integer, name text, price numeric, discounted_price numeric, CHECK (price > 0) CHECK (discounted_price > 0), CHECK (price > discounted_price));
# create table books(book_no integer, name text, price numeric, discounted_price numeric, CHECK (price > 0 and discounted_price > 0 and price > discounted_price));
# 和字段约束一样, 也可以给表约束赋予名称
# create table books(book_no integer, name text, price numeric, discounted_price numeric, CHECK (price > 0) CHECK (discounted_price > 0), CONSTRAINT valid_discount CHECK (price > discounted_price));

# 非空约束
# create table books(book_no integer not null, name text, price numeric);
# 非空约束等效于一个检查约束
# CHECK (column_name IS NOT NULL);
# 一个字段可以有多个约束
# create table books(book_no integer not null, name text, price numeric NOT NULL CHECK(price > 0));

# 唯一约束
# create table books(book_no integer UNIQUE, name text, price numeric);
# 表约束
# create table books(book_no integer, name text, price numeric, UNIQUE(book_no));

# 外键约束
# create table class (class_no int primary key,  class_name varchar(40));
# create table student (student_no int primary key, student_name varchar(40), age int, class_no int REFERENCES class(class_no));

# 修改表
# 增加字段
# alter table class ADD COLUMN class_teacher varchar(40);
# alter table class ADD COLUMN class_teacher varchar(40) CHECK (class_teacher <> '');
# 删除字段
# alter table class drop COLUMN class_teacher;
# 如果想删除外键依赖, 需要通过cascade指明删除任何依赖改字段的东西
# alter table class drop COLUMN class_no;
# 使用cascade会把表student上的外键"student_class_no_fkey"也删除掉:
# alter table class drop COLUMN class_no cascade;

# 增加约束
# alter table student add check (age < 16);
# alter table class add constraint unique_class_teacher UNIQUE (class_teacher);
# 增加非空约束的方法
# alter table student alter COLUMN student_name SET NOT NULL;

# 删除约束
# alter table student drop constraint constraint_name;
# \d student
# 删除约束
# alter table student drop constraint student_age_check;
# 注意非空约束是没有名称的, 需要使用下面的语法去除约束
# alter table student alter column student_name DROP NOT NULL;

# 修改默认值
# alter table student alter column age set default 15;
# 删除默认值
# alter table student alter column age DROP DEFAULT;

# 修改字段数据类型
# alter table student alter column student_name TYPE text;
# 数据长度太小，不能转换
# alter table class alter column class_name TYPE varchar(5);
# 数据类型不对，不能转化
# alter table class alter column class_name TYPE int;
# 改变字段numeric类型的精度是，虽然可能成功，导致精度数据丢失
# select * from books;
# alter table books alter column price TYPE numeric(9, 1);
# 在修改字段类型之前，最好删除这个字段上的约束，修改完后再把合适的约束添加上去。

# 重命名字段
# alter table books RENAME COLUMN book_no TO book_id;
# 重命名表
# alter table class RENAME TO classes;

# 表继承及分区表
# create table persons(name text, sex boolean, age int);
# create table students (class_no int) INHERITS (persons);
# insert into students values("张三", 15, true, 1);
# insert into students values("翠莲", 14, true, 2);
# select * from persons;
# select * from students;
# 更新
# update students set age = 13 where name = '张三';
# select * from persons;
# insert into persons values('王五', 30, true);       # student表中看不到
# 如果只想把父表本身的数据查询出来, 只需要在查询表名前加"ONLY"关键字
# select * from only persons;
# 所有父表的检查约束和非空约束都会自动被所有子表继承。不过其他类型的约束(唯一、主键、外键)则不会被继承。

# 分区表
# create table sales_detail(
#     product_id int not null,    --产品编号
#     price       numeric(12, 2), --单价
#     amount      int not null,   --数量
#     sale_date   date not null,  --销售日期
#     buyer       varchar(40),    --买家名称
#     buyer_contact text          --买家的联系方式
# );


