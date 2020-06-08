#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# django orm中blank和null的区别
# django orm中blank和null的区别
#     blank只是在填写表单的时候可以为空，而在数据库上存储的是一个空字符串；null是在数据库上表现NULL，而不是一个空字符串；
#     需要注意的是，日期型（DateField、TimeField、DateTimeField）和数字型（IntegerField、DecimalField、FloatField）不能接受空字符串，如要想要在填写表单的时候这两种类型的字段为空的话，则需要同时设置null=True、blank=True；
#     另外，设置完null=True后需要重新更新一下数据库。