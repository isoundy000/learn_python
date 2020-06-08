#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

# 1 在普通的pc机上，数组大概占多大内存 int a[1000000]      4M
# 一个bool类型占用1个字节。int 类型占用4个字节。定义的数组的大小等于数组大小size*每个元素的大小。
# 测试方法:
# 用sizeof的方法可以测试出结果。数组也可以用这个来测试。
# 例如sizeof(int)等；
# int a[5];   sizeof(a);
# 全局变量在静态存储区分配内存，局部变量是在栈上分配内存空间的，这么大的数组copy放到栈上不溢出吗？
# VC堆栈默认是1M，int a[1000000]的大小是4*1000000，将近4M，远远大于1M，编译连接的时候不会有问题，但运行是堆栈溢出，程序异常终止。zhidao
# 如果你真的需要在堆栈上使用这么大的数组，那么可以在工程选项链接属性里设置合适的堆栈大小。

# 2 在普通的pc机上，1秒钟可以进行多少次空的for循环？             # 上亿次
# {
#     DWORD startTick = GetTickCount();                  # 获取毫秒数
#
#     int i = 0;
#     for(;;i++)
#     {
#         DWORD endTick = GetTickCount();
#         if((endTick - startTick)/1000 >= 1) break;
#     }
#
#     printf("i = %d\n", i);
#     system("pause");
#     return 0;
# }
# 结果 124911402

# 如果使用while(true)呢？
#include <iostream>
#include <windows.h>
#
# int main()
# {
#     DWORD startTick = GetTickCount();
#
#     int i = 0;
#     while(true)
#     {
#         i++;
#         DWORD endTick = GetTickCount();
#         if((endTick - startTick)/1000 >= 1) break;
#     }
#
#     printf("i = %d\n", i);
#     system("pause");
#     return 0;
# }
# 结果 114612037
# 可以看出1s内for(;;)是比while(true)循环的次数要多的，从原理上解释，for(;;)是空语句，指令少，
# 不占用寄存器，没有判断跳转，比while(true)简洁明了

# 3 进程和线程之间有什么区别和联系？做过多线程编程吗？线程加锁的作用是什么？
# 线程是系统执行的最小的单元
# 进程是系统资源分配的最小单元
# 加锁 是防止多线程同时读写同一份共享资源的时候，引起冲突

# 4 运行结果<32位操作系统>
# #include <stdio.h>
#
# void func(char *str) {
# 	printf("%d %d\n", size(of), strlen(str));
# }
# int main()
# {
#     char a[] = "123456789";
# 	printf("%d", sizeof(a));        # 字符串a的长度是9，字符串a占用的内存空间是10个字符，也就是10个字节。
# 	func(a);
# }

# 5 指定一个文件目录中，怎样查找文件名包含特定字符串的文件？
# ls -l | awk '{print $NF}' | grep "查询字符串"         # NF代表：浏览记录的域的个数   $NF代表：最后一个Field(列)

# 6 指定一个文件目录中，怎样查找内容包含特定字符串的文件？(用命令行或者其他方法)
# grep -ro "xxx" ./*                                    # -o: 只显示匹配到的pattern -r匹配子目录

# 格式：grep [option] PATTERN [FILE...]
# option:
#         -i:忽略大小写
#         -v:取反，显示未被匹配到的pattern
#         -n:显示匹配的行号
#         -c:统计匹配的行数
#         -o: 只显示匹配到的pattern
#         -q: 静默，不予显示
#         -A#:after，匹配到的行再向后显示#行
#         -B#:before，匹配到的行再向前显示#行
#         -C#:context，向前向后各显示#行
#         -E :等同于egrep(扩展的正则表达式)

# 7 在浏览器中输入www.baidu.com, 从输入到网页展示出来，期间发生了哪些过程，详述一下
    # 1.1 用户输入网址，浏览器解析URL后向WEB服务端发送HTTP请求。这里不得不提到http协议：
    # HTTP协议即（超文本传输协议）,是用于从万维网服务器传输超文本到本地浏览器的传送协议。HTTP请求消息格式包括请求头部，消息体，请求数据。如下图：
    # baidu_0.png
    # 1.2.HTTP请求消息生成后。下一步是根据DNS查询IP地址，称为域名解析。全世界有很多DNS服务器，
    # baidu_1.png
    # 些服务器中保存着每个域名所对应的IP地址。就像下图那样，在windows系统中，打开CMD窗口，输入命令“ping www.baidu.com”按回车后返回的就是百度官网的IP地址。
    # 1.3.域名解析后，浏览器将HTTP请求消息发送到百度WEB服务器。服务器返回HTTP响应消息。此消息通过浏览器再次解析并渲染显示大家看到的百度页面。
    # 编后语：此过程以一个前端初学者的角度进行简要概括。另外整个过程涉及到的知识点太多，例如：URL、DNS、HTTP协议、协议栈（套接字）、TCP/IP协议、HTML、CSS、JAVASCRIPT、浏览器、操作系统等。我会更新完善

# 8 谈一下你对设模式的认识和理

# 二 编程题
# 1 请把name、order、score、变量按照格式拼接，放到result里
# char name[16] = "小涛";
# int order = 2;
# float score = 90.5;
# char result[128];
# 小涛同学考试成绩为90.5, 全班排第2名(变量类型转换，字符串拼接)

# 2 字符串反转
b = ''
for i in '12345678'[::-1]:
    b = b + i
print b

# 3 在扑克牌游戏中，需要实现一个查找顺子的算法(连续的数字为顺子)，随机发N张牌，从中挑出最长的顺子，并返回其长度，如果没有顺子返回0
# int cards[16] = {12, 3, 4, 10, 6, 5, 6, 8, 11, 9, 11, 11, 9, 12, 1};
# intgetMaxShunZiLength(int cards[], intcardlen){...}
# 对于上面给出的数据，应该返回最长的顺子: 8, 9, 10, 11, 12的长度5
# 1 去重、排序
m = [12, 3, 4, 10, 6, 5, 6, 8, 11, 9, 11, 11, 9, 12, 1]
m.sort()
s = set(m)
m1 = list(s)
print m1        # [1, 3, 4, 5, 6, 8, 9, 10, 11, 12]
# 2. 不定数循环去找出每个元素连续间隔1的长度, n不断叠加, 找到最大长度
def foo1(m1):
    def foo(m1):
        # 字典作为容器
        m = dict()
        for i in range(len(m1)):
            # 初始长度为1
            n = 1
            # 如果里面条件成立,开始循环
            while 1:
                # 如果下标加上顺子长度大于等于列表长度, 则退出循环
                if i + n >= len(m1):
                    break
                # 如果列表下标 i+n的元素 减去 i的元素, 差值是n, 则长度加1, 字典更新出key和value,
                # 寻找长度加1(因为已经排序了, 所以如果是顺子, 肯定索引差值就等于数值差值)
                elif m1[i + n] - m1[i] == n:
                    max_length = n + 1
                    m['%s' % m1[i]] = max_length
                    n += 1
                # 如果数值差值不等于索引差值, 则长度保留为上一次的差值,  退出循环.
                else:
                    break
        return m

    x = foo(m1)
    cards = []
    # 遍历字典, 找出其中最大长度对应的起始数字, 即可得到该数字延伸长度的顺子组合.
    for key, value in x.items():
        if max(x.values()) == 1:
            return 0
        elif value == max(x.values()):
            cards.append([int(key) + i for i in range(max(x.values()))])
            return '最长顺子为: %s, 长度为:%s' % (cards,max(x.values()))

print foo1(m1)


# 4 写一个函数，给定矩阵的长度级数n，返回一个回旋排列的数字矩阵
# 例如 n=2 返回
# 1 2
# 4 3

# n = 3 返回
# 1 2 3
# 8 9 4
# 7 6 5

# n = 4 返回
# 1  2  3  4
# 12 13 14 5
# 11 16 15 6
# 10 9  8  7

# numpy导入  先在终端下输入pip install numpy，下载第三方包numpy
import pprint
import numpy


def Matrix():
    N = int(input('请输入数字m:'))   # 行
    M = int(input('请输入数字n:'))   # 列
    array = numpy.zeros((N, M), dtype=numpy.int16)

    # 起始点
    x, y = 0, 0                     # x行 y列
    res = array[x][y] = 1           # 行列的点 为1

    while (res < N * M):            # 3 * 3 = 9
        # 改变起始的位置，可以改变旋转，但必须按规律来
        # 上  左-->右
        while (y + 1 < M and not array[x][y + 1]):
            res += 1                # 结果+1
            y += 1                  # 列加1
            array[x][y] = res
        # 右  上-->下
        while (x + 1 < N and (not array[x + 1][y])):
            res += 1
            x += 1
            array[x][y] = res
        # 下  右--->左
        while (y - 1 >= 0 and not array[x][y - 1]):
            res += 1
            y -= 1
            array[x][y] = res
        # 左  下--->上
        while (x - 1 >= 0 and not array[x - 1][y]):
            res += 1
            x -= 1
            array[x][y] = res

    # pprint.pprint(array)
    print(array)


Matrix()

# 三 算法题
# 有两个特别大的手机号码文件，A文件包含100万个号码(每行1个手机号)，B文件包含1000万个号码，请找出A、B文件中共有的手机号码
# (从算法和数据结构角度来思考，大数据量有性能要求，写清解决问题思路即可，可以不写详细代码)