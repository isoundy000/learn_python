# -*- encoding: utf-8 -*-
'''
Created on 2019年11月19日

@author: houguangdong
'''

# Python-struct.error: argument for 's' must be a bytes object
# 我使用的Python3.0版本，运行以下的代码的时候出现了报错。

F = open('data.bin', 'wb')
import struct
data = struct.pack('>i4sh', 7, b'spam', 8)
print(data)
print(struct.calcsize('>i4sh'))
# Python 3.0 struct 格式化字符串
# 在Python 3.0中，格式化字符串的s参数，在Python中的类型是bytes类型。而bytes是3.0中新增的类型之一。
# 表Python3.0给出的表可以看到，c,s,p的Python type都是bytes类型。

# 所以在使用这些类型的时候，要将需要pack的字符串写成bytes型的。

# Python中struct.pack()和struct.unpack()用法详细说明
# python中的struct主要是用来处理C结构数据的，读入时先转换为Python的字符串类型，然后再转换为Python的结构化类型，比如元组(tuple)啥的~。一般输入的渠道来源于文件或者网络的二进制流。
# 1.struct.pack()和struct.unpack()
# 在转化过程中，主要用到了一个格式化字符串(format strings)，用来规定转化的方法和格式。
# 下面来谈谈主要的方法：
# 1.1 struct.pack(fmt,v1,v2,.....)
# 　　将v1,v2等参数的值进行一层包装，包装的方法由fmt指定。被包装的参数必须严格符合fmt。最后返回一个包装后的字符串。
# 1.2 struct.unpack(fmt,string)
# 　　顾名思义，解包。比如pack打包，然后就可以用unpack解包了。返回一个由解包数据(string)得到的一个元组(tuple), 即使仅有一个数据也会被解包成元组。其中len(string) 必须等于 calcsize(fmt)，这里面涉及到了一个calcsize函数。struct.calcsize(fmt)：这个就是用来计算fmt格式所描述的结构的大小。
# 　 格式字符串(format string)由一个或多个格式字符(format characters)组成，对于这些格式字符的描述参照Python manual如下:

# native byteorder
buffer = struct.pack('ihb', 1, 2, 3)
print(repr(buffer))
print(struct.unpack('ihb', buffer))
# data from a sequence, network byteorder
data = [1, 2, 3]
buffer = struct.pack("!ihb", *data)
print(repr(buffer))
print(struct.unpack('!ihb', buffer))
# 首先将参数1,2,3打包，打包前1,2,3明显属于python数据类型中的integer,pack后就变成了C结构的二进制串，转成 python的string类型来显示就是　　'\x01\x00\x00\x00\x02\x00\x03'。由于本机是小端('little- endian',关于大端和小端的区别请参照这里, 故而高位放在低地址段。i 代表C struct中的int类型，故而本机占4位，1则表示为01000000;h 代表C struct中的short类型，占2位，故表示为0200;同理b 代表C struct中的signed char类型，占1位，故而表示为03。
# 其他结构的转换也类似，有些特别的可以参考官方文档的Manual。
# 在Format string 的首位，有一个可选字符来决定大端和小端，列表如下：
# 如果没有附加，默认为@，即使用本机的字符顺序(大端or小端)，对于C结构的大小和内存中的对齐方式也是与本机相一致的(native)，比如有的机器integer为2位而有的机器则为四位;有的机器内存对其位四位对齐，有的则是n位对齐(n未知，我也不知道多少)。
# 还有一个标准的选项，被描述为：如果使用标准的，则任何类型都无内存对齐。
# 比如刚才的小程序的后半部分，使用的format string中首位为！，即为大端模式标准对齐方式，故而输出的为'\x00\x00\x00\x01\x00\x02\x03'，其中高位自己就被放在内存的高地址位了。
# 以上就是Python中struct.pack()和struct.unpack()用法详细说明的详细内容，更多请关注php中文网其它相关文章！