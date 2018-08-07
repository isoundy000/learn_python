#!/usr/bin/env python
#coding: utf-8

# 用一个例子说明使用Python操作PB的方法：
# 1.定义.proto文件。
# 2.编译.proto文件产出Python代码。
# 3.使用Python API读写message。
# 该例子完成一个地址簿程序，能够对地址簿信息进行读写，地址簿中每个人的信息包括姓名、ID、email、联系电话。




import addressbook_pb2 as addressbook
person = addressbook.Person()
person.id = 1234
person.name = "John Doe"
person.email = "jdoe@example.com"
phone = person.phone.add()             # phone字段是符合类型，调用add()方法初始化新实例。如果phone字段是标量类型，直接append()添加新元素即可。
phone.number = "555-4321"
phone.type = addressbook.Person.HOME

# 如果访问.proto文件中未定义的域，抛出AttributeError，如果为某个域赋予了错误类型的值，抛出TypeError。在某个域未赋值前访问该域，返回这个域的默认值。
# 枚举
# 有整型值的符号常量，比如addressbook.Person.WORK的值是2。
# 标准message方法
# person.Clear()
print person.IsInitialized()
print person.name

# 每个Message类含有一些检查或操作整个message的方法，比如：
# • IsInitialized()：检查是否所有required域都已赋值。
# • str()：返回message的可读形式，可以通过str(message)或者print message触发，用于调试代码。
# • Clear()：将所有域的赋值清空。
# • MergeFrom(other_msg)：将给定的other_msg的内容合并到当前message，独立的域使用other_msg的值覆盖写入，repeated域的内容append到当前message的对应字段。独立的子message和group被递归的合并。
# • CopyFrom(other_msg)：先对本message调用Clear()方法，再调用MergeFrom(other_msg)。
# • MergeFromString(serialized)：将PB二进制字符串解析后合并到本message，合并规则与MergeFrom方法一致。
# • ListFields():以(google.protobuf.descriptor.FieldDescriptor，value)的列表形式返回非空的域，独立的域如果HasField返回True则是非空的，repeated域至少包含一个元素则是非空的。
# • ClearField(field_name)：清空某个域，如果被清空的域名不存在，抛出ValueError异常。
# • ByteSize()：返回message占用的空间大小。
# • WichOneof(oneof_group)：返回oneof组中被设置的域的名字或None，如果提供的oneof的组名不存在，抛出ValueError异常。比如test.proto中内容如下：

# message Test {
#     required string a = 1;
#     optional float b = 2;
#     oneof l {
#         string c = 3;
#         int32 d = 4;
#         float e = 5;
#     }
# }

# 调用WhichOneof的代码如下：
#
# import test_pb2 as test
#
# t1 = test.Test()
#
# t1.a = "t1"
# t1.b = 1.0
# t1.c = "oneof c"
# print t1.WhichOneof('l')

# 运行输出：
# c

# 序列化和解析
#
# 每个Message类都有序列化和解析方法：
# • SerializeToString()：将message序列化并返回str类型的结果（str类型只是二进制数据的一个容器而已，而不是文本内容）。如果message没有初始化，抛出message.EncodeError异常。
# • SerializePartialToString()：将message序列化并返回str类型的结果，但是不检查message是否初始化。
# • ParseFromString(data)：从给定的二进制str解析得到message对象。
#
# 如果要在生成的PB类的基础上增加新的功能，应该采用包装（wrapper）的方式，永远不要将PB类作为基类派生子类添加新功能。

# 将message写入文件
#
# import addressbook_pb2
# import sys
#
# def PromptForAddress(person):
#     person.id = int(raw_input("Enter person ID number: "))
#     person.name = raw_input("Enter name: ")
#
#     email = raw_input("Enter email address (blank for none): ")
#     if email != "":
#         person.email = email
#
#     while True:
#         number = raw_input("Enter a phone number (or leave blank to finish): ")
#         if number == "":
#             break
#
#         phone_number = person.phones.add()
#         phone_number.number = number
#
#         type = raw_input("Is this a mobile, home or work phone? ")
#         if type == "mobile":
#             phone_number.type = addressbook_pb2.Person.MOBILE
#         elif type == "home":
#             phone_number.type = addressbook_pb2.Person.HOME
#         elif type == "work":
#             phone_number.type = addressbook_pb2.Person.WORK
#         else:
#             print "Unkown phone type; leaving as default value"
#
# if len(sys.argv) != 2:
#     print "Usage:", sys.argv[0], "ADDRESS_BOOK_FILE"
#     sys.exit(-1)
#
# address_book = addressbook_pb2.AddressBook()
#
# # Read the existing address book.
# try:
#     f = open(sys.argv[1], "rb")
#     address_book.ParseFromString(f.read())
#     f.close()
# except IOError:
#     print sys.argv[1] + ": Could not open file. Creating a new one."
#
# # Add an address.
# PromptForAddress(address_book.people.add())
#
# # Write the new address book back to disk.
# f = open(sys.argv[1], "wb")
# f.write(address_book.SerializeToString())
# f.close()

# 从文件读取message对象
#
# import addressbook_pb2
# import sys
#
# def ListPeople(address_book):
#     for person in address_book.people:
#         print "Person ID:", person.id
#         print " Name:", person.name
#         if person.HasField("email"):
#             print " E-mail adress:", person.email
#
#         for phone_number in person.phones:
#             if phone_number.type == addressbook_pb2.Person.MOBILE:
#                 print " Mobile phone #:",
#             elif phone_number.type == addressbook_pb2.Person.HOME:
#                 print " Home phone #:",
#             elif phone_number.type == addressbook_pb2.Person.WORK:
#                 print " Work phone #:",
#             print phone_number.number
#
# if len(sys.argv) != 2:
#     print "Usage:", sys.argv[0], "ADDRESS_BOOK_FILE"
#     sys.exit(-1)
#
# address_book = addressbook_pb2.AddressBook()
#
# # Read the existing address book
# f = open(sys.argv[1], "rb")
# address_book.ParseFromString(f.read())
# f.close()

# ListPeople(address_book)
# 如果Message.HasField(field_name)的参数对应的域规则是optional，且该域没有设置值，返回False，如果对应的域规则是repeated，且该域没有设置值，抛出ValueError异常。
#
# message的赋值
#
# message中，标量类型和枚举类型的域，必须通过message.field_name=value的格式赋值，message类型的域，可以使用tmp=message.field_name赋值给tmp后，通过操作tmp赋值。当然，message类型的域也可以使用同标量赋值一样的格式赋值。
# 比如test.proto内容为：

# message Test {
#     required inner a = 1;
#     message inner {
#         required string a = 2;
#         optional int32 b =3;
#     }
#     optional Color b = 4;
#     enum Color {
#         RED = 0;
#         GREEN = 1;
#     }
#     optional string c = 5;
# }


# 赋值的代码为：

# import test_pb2 as test
#
# t1 = test.Test()
# t1.c = "scalar"
# a = t1.a
# a.a = "message string"
# a.b = 1
# # 使用如下方式赋值也可以
# # t1.a.a = "message string"
# # t1.a.b = 1
# t1.b = test.Test.RED
# print "t1:\n", t1
