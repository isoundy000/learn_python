#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/30 15:14

# python性能分析之cProfile模块
# -s cumulative
# -s cumulative开关告诉cProfile对每个函数累计花费的时间进行排序, 他能让我看到代码最慢的部分。
# 我们有这样一个函数。
def foo():
    for a in range(0, 101):
        for b in range(0, 101):
            if a + b == 100:
                yield a, b


if __name__ == "__main__":
    for item in foo():
        print(item)

# 运行下面命令
# python3 -m cProfile -s cumulative loopdemo.py
# 其中对参数的解释:
# ncalls：表示函数调用的次数；
# tottime：表示指定函数的总的运行时间，除掉函数中调用子函数的运行时间；
# percall：（第一个percall）等于 tottime/ncalls；
# cumtime：表示该函数及其所有子函数的调用运行的时间，即函数开始调用到返回的时间；
# percall：（第二个percall）即函数运行一次的平均时间，等于 cumtime/ncalls；
# filename:lineno(function)：每个函数调用的具体信息；
# 需要注意的是cProfile很难搞清楚函数内的每一行发生了什么，是针对整个函数来说的。

# -o profile.stats
# 我们可与你通过这个函数将结果输出到一个文件中，当然文件的后缀名是任意的，这里为了方便后面配合python中使用所以将后缀定为stats。
# 首先让我们运行下面的命令
# python3 -m cProfile -o loopdemo_profile.stats loopdemo.py
# 然后运行下面的脚本
import pstats
p = pstats.Stats("loopdemo_profile.stats")
p.sort_stats("cumulative")
p.print_stats()
p.print_callers()       # 可以显示函数被哪些函数调用
p.print_callees()       # 可以显示哪个函数调用了哪些函数

# line_profiler
# pip3 install Cpython
# pip3 install Cython git+https://github.com/rkern/line_profiler.git