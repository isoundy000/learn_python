# -*- encoding: utf-8 -*-
'''
Created on 2019年11月19日 12:25

@author: houguangdong
'''

# python3.x中编码规则：
# byte->str->byte
# byte->str为解码；str->byte为编码
print((204).to_bytes(length=1, byteorder='big'))
print(str(204).encode(encoding='utf-8'))
print('204'.encode())
print(chr(165), chr(204))
print(chr(204).encode())
print(bytes([204]))
print('----------------------------------------')

# str 与 byte 类型编码互转
# 在Python3中的字符串类型：
# 文本字符串类型：
# 即我们通常定义的str类型的对象。在Python3中，str类型的对象都是Unicode，因此对于str类型的对象只有encode（）方法，没有decode（）方法（若运行，会报错）。
# 字节字符串类型：
# 即byte类型的对象。对于该类对象，是由str类型对象使用encode()方法产生，byte对象可以进行解码过程，从而得到真正的内容。
# 避免出现乱码的准则：
# 　　遵循编码使用哪种格式，解码就使用哪种格式。

# str 与 byte 类型互转：
# encode(),将str转换为byte：
test = "我叫林群彬"
# 可以在转换里添加编码方式：encode('utf-8')。解码时，必须要采用这种方式解码('utf-8')
test_encode = test.encode()
print(test_encode)
# b开头的，就是byte类型数据。
# b'\xe6\x88\x91\xe5\x8f\xab\xe6\x9e\x97\xe7\xbe\xa4\xe5\xbd\xac'
print(type(test_encode))
print('----------------------------------------')
# decode()，将byte转换为str：
# 可以在转换里添加解码方式：decode('utf-8')，也可以('utf8')、或者('UTF_8')
print(test_encode.decode('utf8'))
print(type(test_encode.decode()))


a = str(b'\n\x041003\x12\x0210\x1a\x011')
a.encode('utf-8')
print(a)
