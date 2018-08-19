# -*- encoding: utf-8 -*-
'''
Created on 2018年5月21日

@author: houguangdong
'''

# \d 显示数据库中有那些表
# \d score 显示这张表的定义情况
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