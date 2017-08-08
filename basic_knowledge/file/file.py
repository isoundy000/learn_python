# -*- encoding: utf-8 -*-
'''
Created on 2017年4月19日

@author: ghou
'''

# Python File(文件) 方法
# file 对象使用 open 函数来创建，下表列出了 file 对象常用的函数： 
# 1 Python File close() 方法   关闭文件。关闭后文件不能再进行读写操作。
# 概述
# close() 方法用于关闭一个已打开的文件。关闭后的文件不能再进行读写操作， 否则会触发 ValueError 错误。 close() 方法允许调用多次。
# 当 file 对象，被引用到操作另外一个文件时，Python 会自动关闭之前的 file 对象。 使用 close() 方法关闭文件是一个好的习惯。
# 语法
# 
# close() 方法语法如下：
# fileObject.close();
# 
# 实例
# 以下实例演示了 close() 方法的使用：
# 打开文件
fo = open("runoob.txt", "wb")
print "文件名为: ", fo.name
# 关闭文件
fo.close()
# 以上实例输出结果为：
# 文件名为:  runoob.txt

# 2 file.flush()
# 刷新文件内部缓冲，直接把内部缓冲区的数据立刻写入文件, 而不是被动的等待输出缓冲区写入。
# flush() 方法是用来刷新缓冲区的，即将缓冲区中的数据立刻写入文件，同时清空缓冲区，不需要是被动的等待输出缓冲区写入。
# 一般情况下，文件关闭后会自动刷新缓冲区，但有时你需要在关闭前刷新它，这时就可以使用 flush() 方法。

# 打开文件
fo = open("runoob.txt", "wb")
print "文件名为: ", fo.name
# 刷新缓冲区
fo.flush()
# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  runoob.txt

# 3 file.fileno()
# 返回一个整型的文件描述符(file descriptor FD 整型), 可以用在如os模块的read方法等一些底层操作上。
# 打开文件
fo = open("runoob.txt", "wb")
print "文件名为: ", fo.name

fid = fo.fileno()
print "文件描述符为: ", fid

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  runoob.txt
# 文件描述符为:  3

# 4 file.isatty()
# 如果文件连接到一个终端设备返回 True，否则返回 False。
# 打开文件
fo = open("runoob.txt", "wb")
print "文件名为: ", fo.name

ret = fo.isatty()
print "返回值 : ", ret

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  runoob.txt
# 返回值 :  False

# 5 Python File next() 方法
# 概述
# next() 方法在文件使用迭代器时会使用到，在循环中，next()方法会在每次循环中调用，该方法返回文件的下一行，如果到达结尾(EOF),则触发 StopIteration
# 打开文件
fo = open("runoob.txt", "rw+")
print "文件名为: ", fo.name

for index in range(5):
    line = fo.next()
    print "第 %d 行 - %s" % (index, line)
# 关闭文件
fo.close()

# 6 file.read([size])
# 从文件读取指定的字节数，如果未给定或为负则读取所有。
# 打开文件
fo = open("runoob.txt", "rw+")
print "文件名为: ", fo.name

line = fo.read(10)
print "读取的字符串: %s" % (line)

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  runoob.txt
# 读取的字符串: 1:www.runo

# 7 file.readline([size])
# 读取整行，包括 "\n" 字符。
# readline() 方法用于从文件读取整行，包括 "\n" 字符。如果指定了一个非负数的参数，则返回指定大小的字节数，包括 "\n" 字符。
# 打开文件
fo = open("runoob.txt", "rw+")
print "文件名为: ", fo.name

line = fo.readline()
print "读取第一行 %s" % (line)

line = fo.readline(5)
print "读取的字符串为: %s" % (line)

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  runoob.txt
# 读取第一行 1:www.runoob.com
# 读取的字符串为: 2:www

# 8   file.readlines([sizehint])
# 读取所有行并返回列表，若给定sizeint>0，返回总和大约为sizeint字节的行, 实际读取值可能比sizhint较大, 因为需要填充缓冲区。 如果碰到结束符 EOF 则返回空字符串。
# 打开文件
fo = open("runoob.txt", "rw+")
print "文件名为: ", fo.name

line = fo.readlines()
print "读取的数据为: %s" % (line)

line = fo.readlines(2)
print "读取的数据为: %s" % (line)

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  runoob.txt
# 读取的数据为: ['1:www.runoob.com\n', '2:www.runoob.com\n', '3:www.runoob.com\n', '4:www.runoob.com\n', '5:www.runoob.com\n']
# 读取的数据为: []

# 9    file.seek(offset[, whence])  设置文件当前位置
# seek() 方法用于移动文件读取指针到指定位置。
# 
# 参数
#     offset -- 开始的偏移量，也就是代表需要移动偏移的字节数
#     whence：可选，默认值为 0。给offset参数一个定义，表示要从哪个位置开始偏移；0代表从文件开头开始算起，1代表从当前位置开始算起，2代表从文件末尾算起。

# 打开文件
fo = open("runoob.txt", "rw+")
print "文件名为: ", fo.name

line = fo.readline()
print "读取的数据为: %s" % (line)

# 重新设置文件读取指针到开头
fo.seek(0, 0)
line = fo.readline()
print "读取的数据为: %s" % (line)

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  runoob.txt
# 读取的数据为: 1:www.runoob.com
# 读取的数据为: 1:www.runoob.com

# 10    file.tell() 返回文件当前位置
# tell() 方法返回文件的当前位置，即文件指针当前位置。

# 打开文件
fo = open("runoob.txt", "rw+")
print "文件名为: ", fo.name

line = fo.readline()
print "读取的数据为: %s" % (line)

# 获取当前文件位置
pos = fo.tell()
print "当前位置: %d" % (pos)

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  runoob.txt
# 读取的数据为: 1:www.runoob.com
# 当前位置: 17

# 11    file.truncate([size]) 截取文件，截取的字节通过size指定，默认为当前文件位置。 
# truncate() 方法用于截断文件，如果指定了可选参数 size，则表示截断文件为 size 个字符。 如果没有指定 size，则从当前位置起截断；截断之后 size 后面的所有字符被删除。
# size -- 可选，如果存在则文件截断为 size 字节。 

# 打开文件
fo = open("runoob.txt", "r+")
print "文件名为: ", fo.name

line = fo.readline()
print "读取第一行: %s" % (line)

# 截断剩下的字符串
fo.truncate()

# 尝试再次读取数据
line = fo.readline()
print "读取数据: %s" % (line)

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  runoob.txt
# 读取第一行: 1:www.runoob.com
# 读取数据:

# 以下实例截取 runoob.txt 文件的10个字节：
# 打开文件
fo = open("runoob.txt", "r+")
print "文件名为: ", fo.name

# 截取10个字节
fo.truncate(10)

str = fo.read()
print "读取数据: %s" % (str)

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  runoob.txt
# 读取数据: 1:www.runo

# 12    file.write(str) 将字符串写入文件，没有返回值。
# write() 方法用于向文件中写入指定字符串。
# 在文件关闭前或缓冲区刷新前，字符串内容存储在缓冲区中，这时你在文件中是看不到写入的内容的
# 参数
#     str -- 要写入文件的字符串。

# 打开文件
fo = open("test.txt", "w")
print "文件名为: ", fo.name
str = "菜鸟教程"
fo.write( str )

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  test.txt
# 查看文件内容：
# $ cat test.txt 
# 菜鸟教程

# 13    file.writelines(sequence)
# 向文件写入一个序列字符串列表，如果需要换行则要自己加入每行的换行符。
# 概述
# writelines() 方法用于向文件中写入一序列的字符串。
# 这一序列字符串可以是由迭代对象产生的，如一个字符串列表。
# 换行需要制定换行符 \n。
# 参数
#     str -- 要写入文件的字符串序列。

# 打开文件
fo = open("test.txt", "w")
print "文件名为: ", fo.name
seq = ["菜鸟教程 1\n", "菜鸟教程 2"]
fo.writelines( seq )

# 关闭文件
fo.close()

# 以上实例输出结果为：
# 文件名为:  test.txt
# 查看文件内容：
# $ cat test.txt 
# 菜鸟教程 1
# 菜鸟教程 2