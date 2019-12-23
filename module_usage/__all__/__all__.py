#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time: 2019/12/4 10:00
# @version: 0.0.1
# @Author: houguangdong
# @File: __all__.py
# @Software: PyCharm


# 用 __all__ 暴露接口，这是一种约定
# Python 可以在模块级别暴露接口：
import os, sys

__all__ = ["process_xxx", "bar", "baz"]  # 排除了 `os` 和 `sys`


waz = 5
bar = 10
def baz():
    return 'baz'


def process_xxx():
    pass  # omit


# 控制 from xxx import * 的行为
# 　　 代码中当然是不提倡用 from xxx import * 的写法的，但是在 console 调试的时候图个方便还是很常见的。
#     如果一个模块 spam 没有定义 __all__，执行 from spam import * 的时候会将 spam 中非下划线开头的成员都导入当前命名空间中，
#     这样当然就有可能弄脏当前命名空间。如果显式声明了 __all__，import * 就只会导入 __all__ 列出的成员。如果 __all__ 定义有误，
#     列出的成员不存在，还会明确地抛出异常，而不是默默忽略。

# 3、为 lint 工具提供辅助
# 　　编写一个库的时候，经常会在 __init__.py 中暴露整个包的 API，而这些 API 的实现可能是在包中其他模块中定义的。如果我们仅仅这样写：
# from foo.bar import Spam, Egg
# 　　一些代码检查工具，如 pyflakes 就会报错，认为 Spam 和 Egg 是 import 了又没被使用的变量。当然一个可行的方法是把这个警告压掉：
# 　　from foo.bar import Spam, Egg  # noqa
# 　　但是更好的方法是显式定义 __all__，这样代码检查工具会理解这层意思，就不再报 unused variables 的警告：
# from foo.bar import Spam, Egg
# 　　__all__ = ["Spam", "Egg"]
# 　　需要注意的是大部分情况下 __all__ 都是一个 list，而不是 tuple 或者其他序列类型。如果写了其他类型的 __all__，如无意外 pyflakes 等 lint 工具会无法识别出。
#
# 4、定义 all 需要注意的地方
#
# 如上所述，__all__ 应该是 list 类型的
# 不应该动态生成 __all__，比如使用列表解析式。__all__ 的作用就是定义公开接口，如果不以字面量的形式显式写出来，就失去意义了。
# 即使有了 __all__ 也不应该在非临时代码中使用 from xxx import * 语法，或者用元编程手段模拟 Ruby 的自动 import。Python 不像 Ruby，没有 Module 这种成员，模块就是命名空间隔离的执行者。如果打破了这一层，而且引入诸多动态因素，生产环境跑的代码就充满了不确定性，调试也会非常困难。
# 按照 PEP8 建议的风格，__all__ 应该写在所有 import 语句下面，和函数、常量等模块成员定义的上面。
# 　　如果一个模块需要暴露的接口改动频繁，__all__ 可以这样定义：　
#
# __all__ = [
#     "foo",
#     "bar",
#     "egg",
# ]
# 　　最后多出来的逗号在 Python 中是允许的，也是符合 PEP8 风格的。这样修改一个接口的暴露就只修改一行，方便版本控制的时候看 diff。

