# -*- encoding: utf-8 -*-
'''
Created on 2019年11月4日

@author: houguangdong
'''

# Python type hints 之 Optional，Union
# 本文链接：https://blog.csdn.net/ypgsh/article/details/84992461
# 1，前言

# type hint 在pep484加入，我个人觉得这种类似于类型约束的（机制）有点违背了python简单、简洁的初衷，在慢慢向c# java 这种强类型语言看齐的节奏。
# 不过好在不强制使用，个人觉得依照规则编码也有点好处，
# 一方面，因为输入输出的类型进行定义的过程中，推动个人对输入输出进行详细的思考，个人的思路也会更清晰， 写的函数不容易飘。
# 另一方面，当代码量大的时候，可以借助工具进行检查，提前知道bug。
# 最后，也起到了docstring的作用，交流的时候，别人也更容易理解， 过了很长时间自己忘得差不多回过头看的时候，也能很快回忆起来。
# 2，type hints 类型
# type hints 主要是要指示函数的输入和输出的数据类型，数据类型在typing包中，基本类型有str list dict等等，
# 使用示例：
# def hello(name: str) -> None:
#     print('hello {}'.format(name))
# type hints 有很多别的类型，此处主要说Union，Optional， 因为对于python 用到的也比较多
# Union是当有多种可能的数据类型时使用，比如函数有可能根据不同情况有时返回str或返回list，那么就可以写成Union[list, str]
# Optional是Union的一个简化， 当
# 数据类型中有可能是None时，比如有可能是str也有可能是None，则Optional[str], 相当于Union[str, None]. ** 注意 ** 和
# 函数有默认参数None有区别，有区别，有区别，不可省略默认参数，如下示例：
# 原始：def func(args=None):
# 错：def func(args: Optional[str]) -> None:
# 对：def func(args: Optional[str] = None) -> None:
# type hints 还可以自定义类型等等