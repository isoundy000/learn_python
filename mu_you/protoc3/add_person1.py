#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/1 13:35
# @version: 0.0.1
# @Author: houguangdong
# @File: add_person1.py
# @Software: PyCharm

from mu_you.protoc3 import addressbook1_pb2

address_book = addressbook1_pb2.AddressBook()
person = address_book.people.add()

person.id = 1
person.name = "safly"
person.email = "safly@qq.com"
person.money = 1000.11

person.work_status = True

phone_number = person.phones.add()
phone_number.number = "123456"
phone_number.type = addressbook1_pb2.MOBILE

maps = person.maps.add()
maps.mapfield[1] = 1
maps.mapfield[2] = 2

hobby = person.hobby.add()
hobby.interest = "python"


#序列化
serializeToString = address_book.SerializeToString()
print(serializeToString, type(serializeToString))



address_book.ParseFromString(serializeToString)

for person in address_book.people:
  print("p_id{},p_name{},p_email{},p_money{},p_workstatu{}"
        .format(person.id, person.name, person.email, person.money, person.work_status))

  for phone_number in person.phones:
        print(phone_number.number, phone_number.type)
  print(person.phones[0].number)


for map in person.maps:
    for key in map.mapfield:
        print(key, '-------', map.mapfield[key])

    for hobby in person.hobby:
        print(hobby.interest)