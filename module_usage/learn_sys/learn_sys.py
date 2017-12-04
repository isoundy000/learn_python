#-*-coding:utf-8-*-
'''
Created on 2017年9月15日

@author: houguangdong
'''
# 关于python的最大递归层数详解
# 在阅读http://www.cnblogs.com/skabyy/p/3451780.html这篇文章的时候，实验yield的流式迭代素数的时候发现有个问题，故详细记录下来。
# 首先来看看python默认的最大递归层数：


def foo(n):
    print(n)
    n += 1
    foo(n)

 
if __name__ == '__main__':
    foo(1)

# 得到的最大数为998，以后就是报错了：RecursionError: maximum recursion depth exceeded while calling a Python object
# 那么python允许的最大递归层数是多少呢？我们实验下：
# 复制代码
import sys
sys.setrecursionlimit(100000)


def foo1(n):
    print(n)
    n += 1
    foo1(n)
        
if __name__ == '__main__':
    foo1(1)


# 得到的最大数字在3925-3929之间浮动，这个是和计算机有关系的，不然也不会是一个浮动的数字了（数学逻辑讲求严谨）。
# 我们已经将数字调到足够大了，已经大于系统堆栈，python已经无法支撑到太大的递归了。
# 对于没有尾递归的编程语言来说，程序运行起来的时候计算机会给当前进程分配栈，每递归一次，计算机就会给当前程序调度一部分来使用，当使用过多了，那么不好意思，我就这么点了。然后，就没有然后了，崩了。python不是尾递归优化的语言，我们不应该使用递归来替代掉循环，循环存在必然有它巨大的意义。递归用于复杂度为O(log(n))的计算是很有意义的，用于O(n)就不怎么好了。
# 那么有什么好的解决办法呢？当然是有的，比如python的generator，这个是python的一大神器，请参看：http://www.jianshu.com/p/d36746ad845d
# 总结：
# 递归是一个很有用的处理方式，简单到遍历文件夹、处理XML；复杂到人工智能等。
# 合理使用递归能让我们的程序具有简洁和强的可读性。