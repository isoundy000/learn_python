# -*- encoding: utf-8 -*-
'''
Created on 2018年5月21日

@author: houguangdong
'''
# su - postgres         切换用户 数据库默认用户
# psql                  进入数据库命令行客户端
# \l                    展示所有的数据库
# \c xxxx               切换数据库
# \d                    显示数据库中有那些表
# \d score              显示这张表的定义情况
# create table student (no int primary key, student_name varchar(40), age int);
# drop table table_name
# insert into student values(1, 'zhangsan', 14);
# insert into student (no, age, student_name) values(1, 'zhangsan', 14);
# insert into student (no, student_name) values(2, 'wang 2');
# update student set age = 15;
# update student set age = 13, student_name='zhao 4' where no = 2;
# delete from student where no = 3;
# delete from student;              # 删除整张表
# select age + 5 from student;
# select age, 3 + 5 from student;
# select 55 + 88;
# select 10*2, 3*5+2;
# select * from student where age >= 15 order by age, student_name;
# select * from student order by age desc, student_name;
# select age, count(*) from student group by age;       # 使用group by语句时候，需要使用聚合函数, count(*) sum(*)等
# create table class (no int primary key, class_name varchar(40));
# insert into class values(1, '初二(1)班');
# insert into class values(2, '初二(2)班');
# insert into class values(3, '初二(3)班');
# insert into class values(4, '初二(4)班');
# create table student (no int primary key, student_name varchar(40), age int, class_no int);
# insert into student values(1, '张三', 14, 1);
# insert into student values(2, '吴二', 15, 1);
# insert into student values(3, '李四', 13, 2);
# insert into student values(4, '吴三', 15, 2);
# insert into student values(5, '王二', 15, 3);
# insert into student values(6, '李三', 14, 3);
# select stu.name, class.no from student, class where student.class_no = class.no and age>15;
# create table student_bak (no int primary key, student_name varchar(40), age int, class_no int);
# insert into student_bak select * from student;
# 如何把2张表中查询出来的数据整合在一个结果集下
# select * from student where no = 1 union select * from student_bak where no = 2;
# union可以把结果集中相同的两条记录合并成一条
# select * from student where no=1 union select * from student_bak where no = 1;
# 如果不想合并，请使用union all
# select * from student where no=1 union all select * from student_bak where no = 1;
# 情况数据 速度快
# truncate table student_bak;