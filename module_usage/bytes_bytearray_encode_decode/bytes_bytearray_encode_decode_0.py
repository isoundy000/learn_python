#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# python bytes和bytearray、编码和解码

# str、bytes和bytearray简介
# str是字符数据，bytes和bytearray是字节数据。它们都是序列，可以进行迭代遍历。str和bytes是不可变序列，bytearray是可变序列，可以原处修改字节。
# bytes和bytearray都能使用str类型的通用函数，比如find()、replace()、islower()等，不能用的是str的格式化操作。
# 所以，如有需要，参考字符串(string)方法整理来获取这些函数的使用方法。
import sys
print sys.getdefaultencoding()

a = "我"
print a

print ord(a)
print a.encode()

# bytes是不可变的二进制格式字节数据
B = b"abcd"
print [i for i in B]
# B[0] = "A"
print b'abcd'.replace(b'cd', b'XY')


S = b"abcd"
BA = bytearray(S)

print [ i for i in BA ]

BA[0] = 65
print BA


U = u"我爱你"
B = bytes(U, "utf-8")
BA = bytearray(U, "utf-8")
print B, BA

# 编码：str   --> bytes
# 解码：bytes --> str

# 实际上，字符串类型只有encode()方法，没有decode()方法，而bytes类型只有decode()方法而没有encode()方法。
print set( dir(str) ) - set( dir(bytes) )
print set( dir(bytes) ) - set( dir(str) )

# 二进制格式的数据也常称为裸数据(raw data)，所以str数据经过编码后得到raw data，raw data解码后得到的str。
# 编码时，可以使用字节类型的构造方法bytes()、bytearray()来构造字节，也可以使用str类型的encode()方法来转换。
# 解码时，可以使用str类型的构造方法str()来构造字符串，也可以使用bytes、bytearray()类型的decode()方法。
# 另外需要注意的是，编码和解码的过程中都需要指定编码表(字符集)，默认采用的是utf-8字符集。

# 编码过程


# 例如，使用encode()的方式将str编码为bytes数据。
str1 = "abcd"
str2 = "我爱你"

# 默认编码
str1.encode()
str2.encode()

# 显式指定使用utf-8进行编码
str1.encode("utf-8")
str2.encode("utf-8")

# 使用utf-16编码
str1.encode("utf-16")
str2.encode("utf-16")

# 使用gb2312编码
str1.encode("gb2312")
str2.encode("gb2312")

# 使用gbk编码
str1.encode("gbk")
str2.encode("gbk")

# 使用bytes()和bytearray()将str构造成bytes或bytearray数据，这两个方法都要求str->byte的过程中给定编码。

bytes(str1, encoding="utf-8")
bytes(str1, encoding="utf-16")
bytearray(str1, encoding="utf-8")
bytearray(str2, encoding="utf-8")

# 实际上，bytes()、bytearray()这两个方法构造字节数据的时候还有点复杂，因为可以从多个数据源来构造，比如字符串、整数值、buffer。如何使用这两个方法构造字节数据，详细内容参考help(bytes)和help(bytearray)给出的说明，这里给几个简单示例。
# 构造bytes的方式：

# 构造空bytes对象
bytes()

# 使用str构造bytes序列，需要指定编码
bytes("abcd",encoding="utf-8")

# 使用int初始化5个字节的bytes序列
bytes(5)

# 使用可迭代的int序列构造字节序列
# int值必须为0-256以内的数
bytes([65,66,67])

# 使用bytes或buffer来构造bytes对象
bytes(b'abcd')

# 构造bytearray的方式：
# 构造空bytearray对象
print bytearray()

# 使用bytes或buffer构造bytearray序列
print bytearray(b"abcd")

# 使用str构造bytearray序列，需要指定编码
print bytearray("abcd",encoding="utf-8")

# 使用int初始化5个字节的bytearray序列
print bytearray(5)

# 使用可迭代的int序列构造bytearray序列
# int值必须为0-256以内的数
print bytearray([65,66,67])


# 解码过程
# 解码是字节序列到str类型的转换。
# 例如，使用decode()方法进行解码"我"字，它的utf-8的编码对应为"\xe6\x88\x91"：

b = b'\xe6\x88\x91'
# 采用默认字符集utf-8
b.decode()

# 显式指定编码表
b.decode("utf-8")

# 使用str()进行转换。
str(b,"utf-8")

# 关于乱码
# 当编码、解码的过程使用了不同的(不兼容的)编码表时，就会出现乱码。所以，解决乱码的唯一方式是指定对应的编码表进行编码、解码。
# 例如，使用utf-8编码"我"字，得到一个bytes序列，然后使用gbk解码这个bytes序列。
print "我".encode().decode("gbk")

# 这里报错了，因为utf-8的字节序列里有gbk无法解码的字节。如果使用文本编辑器一样的工具去显化这个过程，得到的将是乱码字符。