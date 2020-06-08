#  stackless python初体验
# stackless python真是毁三观，算斐波那契数列，n为100000（十万），运行时间2。2秒左右
# 这里写一下感悟：
# stackless python从字面上理解就是没有栈的python，怎么做到没有栈呢？基于堆栈的语言是怎么实现的：
# 1、一般将函数的调用推进栈里面，后入栈单元计算完之后，先入栈的才能够完成
# 2、栈里面的单元怎么通信呢？今天刚好做完DDos攻击的实验，提醒我了这点：栈的单元通过入口地址和返回地址与它的前后单元通信。
# 3、栈的厚度有限制，貌似是1000多，就是说，迭代到1000多层就不能继续进栈了，当然可以将层数认为调高。大概原理就是这样。
#
# stackless python说，我不要栈！那么不用栈是怎么写程序呢？
# 1、他用一种叫做tasklet的东西代替了堆栈里面的单元
# 2、这些单元通过一种叫做channel的机制来通信
# 3、因为不是基于堆栈，所以这些tasklet的数量你想要多少有多少，就像这里，100000
#
# tasklet又叫做微线程（microthread），所以说，是在python进程里面的一个线程再分出来的“thread”。它被设计为在各个tasklet之间的切换开销远远小于系统的线程。
# 一个tasklet可以通过往另外一个tasklet的channel来发送信息，自己进入阻塞状态，然后激活另一个tasklet
#
# 以斐波那契数列为例：
# 往常，我们使用递归求斐波那契数列的时候。。。。。就不说了，大家都懂
# 如果换做stackless的版本呢？
# 堆栈没了，我们有一个个的tasklet，这些tasklet里面包含了一个channel，一个个的tasklet
# 通过将自己的channel传给下一个tasklet，下一个channel通过将自己的处理结果发送到前一个tasklet的channel里面实现通信。
#
# 其实如果用“微线程”的方式去理解tasklet，你可以认为，它其实是有“堆栈”的，就像系统级别的线程一样，但是这个堆栈仅仅是用于调用一个函数，或者说，将这个函数的调用放进一个tasklet里面。
#
# 通过这种方式（其实我不知道自己说明白没有。。），就形成了一条tasklet链，如果我们将他们想象成层叠的形状，其实跟堆栈的形状也是挺相似的，但是他们不叫堆栈，叫做tasklet，而且性能比堆栈的性能要好。记住这种工具的名字，它叫做stackless python。
#
# 下面是计算斐波那契数列的代码：
# import stackless
#
# dic = {}
#
# def factorial(n):
# if n == 1:
# return 1
# elif n == 2:
# return 2
# else:
# return task(n-1) + task(n-2)
#
#
# def task(n):
# if str(n) in dic:
# return dic[str(n)]
# chann = stackless.channel()
# stackless.tasklet(compute)(n,chann)
# result = chann.receive()
# dic[str(n)] = result
# return result
#
# def compute(n,chann):
# return chann.send(factorial(n))
#
#
# print factorial(100000)
#
# 然后用堆栈版本试了一下，先将python堆栈的层数上线改了100000，运行，大概1.3秒到1.5秒，其实stackless与堆栈相比没有多大优势。
#
# 堆栈版本代码：
# import sys
# sys.setrecursionlimit(100000)
#
# dic = {}
#
# def factorial(n):
# if n == 1:
# return 1
# elif n == 2:
# return 2
# elif str(n) in dic:
# return dic[str(n)]
# else:
# a = factorial(n-1)
# if str(n-1) not in dic:
# dic[str(n-1)] = a
# b = factorial(n-2)
# if str(n-2) not in dic:
# dic[str(n-2)] = a
# return a + b
#
#
# print factorial(99999)
#
# 这里仅仅讲到的是stackless的这么一种用法，一般stackless的用途还是在替代系统线程这方面，用来做并发有c语言级别的性能，这个以后再做测试