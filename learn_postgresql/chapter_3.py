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
# select age + 5 from student;
# select age, count(*) from student group by age;
# select stu.name, class.no from student, class where student.class_no = class.no and age>15;
# insert into student_bak select * from student;
# 如何把2张表中查询出来的数据整合在一个结果集下
# select * from student where no = 1 union select * from student_bak where no = 2;
# union可以把结果集中相同的两条记录合并成一条
# select * from student where no=1 union select * from student_bak where no = 1;
# 如果不想合并，请使用union all
# select * from student where no=1 union all select * from student_bak where no = 1;
# truncate table student_bak;