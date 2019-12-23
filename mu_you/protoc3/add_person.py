#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/1 11:24
# @version: 0.0.1
# @Author: houguangdong
# @File: add_person.py
# @Software: PyCharm

from mu_you.protoc3 import addressbook_pb2

address_book = addressbook_pb2.AddressBook()
person = address_book.people.add()

person.id = 1
person.name = "ghou"
person.email = "ghou@qq.com"
person.money = 1000.11
person.work_status = True

phone_number = person.phones.add()
phone_number.number = "123456"
phone_number.type = addressbook_pb2.MOBILE

maps = person.maps
maps.mapfield[1] = 1
maps.mapfield[2] = 2

# 序列化
serializeToString = address_book.SerializeToString()
print(serializeToString, type(serializeToString))


address_book.ParseFromString(serializeToString)

for person in address_book.people:
    print("p_id{}, p_name{}, p_email{}, p_money{}, p_workstatu{}"
        .format(person.id, person.name, person.email, person.money, person.work_status))

    for phone_number in person.phones:
        print(phone_number.number,phone_number.type)

    for key in person.maps.mapfield:
        print(key, person.maps.mapfield[key])