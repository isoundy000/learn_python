#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
Created on 7/28/2017

@author: houguangdong
'''
# Python本身就内置了很多非常有用的模块，只要安装完毕，这些模块就可以立刻使用。
# 
# 我们以内建的sys模块为例，编写一个hello的模块：
# 
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# 
# ' a test module '
# 
# __author__ = 'Michael Liao'
# 
# import sys
# 
# def test():
#     args = sys.argv
#     if len(args)==1:
#         print('Hello, world!')
#     elif len(args)==2:
#         print('Hello, %s!' % args[1])
#     else:
#         print('Too many arguments!')
# 
# if __name__=='__main__':
#     test()
# 
# 第1行和第2行是标准注释，第1行注释可以让这个hello.py文件直接在Unix/Linux/Mac上运行，第2行注释表示.py文件本身使用标准UTF-8编码；
# 
# 第4行是一个字符串，表示模块的文档注释，任何模块代码的第一个字符串都被视为模块的文档注释；
# 
# 第6行使用__author__变量把作者写进去，这样当你公开源代码后别人就可以瞻仰你的大名；
# 
# 以上就是Python模块的标准文件模板，当然也可以全部删掉不写，但是，按标准办事肯定没错。
# 
# 后面开始就是真正的代码部分。
# 
# 你可能注意到了，使用sys模块的第一步，就是导入该模块：
# 
# import sys
# 
# 导入sys模块后，我们就有了变量sys指向该模块，利用sys这个变量，就可以访问sys模块的所有功能。
# 
# sys模块有一个argv变量，用list存储了命令行的所有参数。argv至少有一个元素，因为第一个参数永远是该.py文件的名称，例如：
# 
# 运行python3 hello.py获得的sys.argv就是['hello.py']；
# 
# 运行python3 hello.py Michael获得的sys.argv就是['hello.py', 'Michael]。
# 
# 最后，注意到这两行代码：
# 
# if __name__=='__main__':
#     test()
# 
# 当我们在命令行运行hello模块文件时，Python解释器把一个特殊变量__name__置为__main__，而如果在其他地方导入该hello模块时，if判断将失败，因此，这种if测试可以让一个模块通过命令行运行时执行一些额外的代码，最常见的就是运行测试。
# 
# 我们可以用命令行运行hello.py看看效果：
# 
# $ python3 hello.py
# Hello, world!
# $ python hello.py Michael
# Hello, Michael!
# 
# 如果启动Python交互环境，再导入hello模块：
# 
# $ python3
# Python 3.4.3 (v3.4.3:9b73f1c3e601, Feb 23 2015, 02:52:03) 
# [GCC 4.2.1 (Apple Inc. build 5666) (dot 3)] on darwin
# Type "help", "copyright", "credits" or "license" for more information.
# >>> import hello
# >>>
# 
# 导入时，没有打印Hello, word!，因为没有执行test()函数。
# 
# 调用hello.test()时，才能打印出Hello, word!：
# 
# >>> hello.test()
# Hello, world!
# 
# 作用域
# 
# 在一个模块中，我们可能会定义很多函数和变量，但有的函数和变量我们希望给别人使用，有的函数和变量我们希望仅仅在模块内部使用。在Python中，是通过_前缀来实现的。
# 
# 正常的函数和变量名是公开的（public），可以被直接引用，比如：abc，x123，PI等；
# 
# 类似__xxx__这样的变量是特殊变量，可以被直接引用，但是有特殊用途，比如上面的__author__，__name__就是特殊变量，hello模块定义的文档注释也可以用特殊变量__doc__访问，我们自己的变量一般不要用这种变量名；
# 
# 类似_xxx和__xxx这样的函数或变量就是非公开的（private），不应该被直接引用，比如_abc，__abc等；
# 
# 之所以我们说，private函数和变量“不应该”被直接引用，而不是“不能”被直接引用，是因为Python并没有一种方法可以完全限制访问private函数或变量，但是，从编程习惯上不应该引用private函数或变量。
# 
# private函数或变量不应该被别人引用，那它们有什么用呢？请看例子：
# 
# def _private_1(name):
#     return 'Hello, %s' % name
# 
# def _private_2(name):
#     return 'Hi, %s' % name
# 
# def greeting(name):
#     if len(name) > 3:
#         return _private_1(name)
#     else:
#         return _private_2(name)
# 
# 我们在模块里公开greeting()函数，而把内部逻辑用private函数隐藏起来了，这样，调用greeting()函数不用关心内部的private函数细节，这也是一种非常有用的代码封装和抽象的方法，即：
# 
# 外部不需要引用的函数全部定义成private，只有外部需要引用的函数才定义为public。

# "if __name__ == '__main__': " 实现的功能就是Make a script both importable and executable
# 关于代码if name == 'main': 可能看了之后可能挺晕的，下面举几个例子解释下，希望能让大家对这行的代码的功能有更深的认识，还是那句话，欢迎大家指正定会虚心接受。
# 
# 先编写一个测试模块atestmodule.py
# 
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# 
# ' a test module '
# 
# def addFunc(a,b):  
#     return a+b  
# 
# print('atestmodule计算结果:',addFunc(1,1))
# 
# 再编写一个模块anothertestmodule.py来调用上面的模块：
# 
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# 
# ' a test module '
# 
# import atestmodule
# 
# print('调用anothermodule模块执行的结果是：',atestmodule.addFunc(12,23))
# 
# 在刚才两个模块的路径（我的路径为：“C:\work”）中打开cmd，用命令行运行atestmodule.py：
# 
# C:\work>python atestmodule.py
# atestmodule计算结果: 2
# 
# 在刚才两个模块的路径中打开，用命令行运行anothertestmodule.py：
# 
# C:\work>python anothertestmodule.py
# atestmodule计算结果: 2
# 调用test模块执行的结果是： 35
# 
# #显然，当我运行anothertestmodule.py后第一句并不是调用者所需要的，为了解决这一问题，Python提供了一个系统变量：__name__
# 
# #注：name两边各有2个下划线__name__有2个取值：当模块是被调用执行的，取值为模块的名字；当模块是直接执行的，则该变量取值为：__main__
# 
# 于是乎，被调用模块的测试代码就可以写在if语句里了，如下：
# 
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# 
# ' a test module '
# 
# def addFunc(a,b):  
#     return a+b  
# 
# if __name__ == '__main__':  
#     print('atestmodule计算结果:',addFunc(1,1))
# 
# 当再次运行atestmodule.py：
# 
# C:\work>python atestmodule.py
# atestmodule计算结果: 2
# 
# #结果并没有改变，因为调用atestmodule.py时，__name__取值为__main__，if判断为真，所以就输出上面的结果
# 
# 当再次运行atestmodule.py：
# 
# C:\work>python anothertestmodule.py
# 调用test模块执行的结果是： 35
# 
# #此时我们就得到了预期结果，不输出多余的结果。能实现这一点的主要原因在于当调用一个module时，此时的__name__取值为模块的名字，所以if判断为假，不执行后续代码。
# 
# 所以代码if name == 'main': 实现的功能就是Make a script both importable and executable，也就是说可以让模块既可以导入到别的模块中用，另外该模块自己也可执行。

# 参考了几篇博文和StackOverFlow
# 
#     名字中没有前后下划线修饰的对象默认为 公有public, 内外皆可随意引用
# 
#     单下划线前缀 _x
#     以单下划线做前缀的名称指定了这个名称是惯例意义上的“私有, private”, 不应该被直接引用    
#     在 有些 导入import * 的场景中，下一个使用你代码的人（或者你本人）会明白这个名称仅内部使用。虽然依然可以被类外访问.
#     之所以说在在 有些 import * 的场景，是因为导入时解释器确实对单下划线开头的名称做了处理。如果你这么写from <module/package> import *，任何以单下划线开头的名称都不会被导入，除非模块/包的__all__列表明确包含了这些名称
#     父类的 _x 在子类中可以直接访问(虽然在类外也可以被类的用户直接访问), 姑且可以当做可以在类内或同类对象中使用的@protected成员 
#     解释:
#     之所以说，但下划线修饰名字的private函数和变量“不应该”被直接引用，而不是“不能”被直接引用，是因为Python并没有一种方法可以完全限制访问private函数或变量，但是，从编程习惯上不应该引用private函数或变量。
#     使用:
#     外部不需要引用的对象,如私有的函数对象,应该全部定义成private，只有外部需要引用的对象才定义为public
# 
#     双下划线前缀 __x
#     如果成员的名字带有, 例如 __population,则 python 将使用名字混淆机制有效的将其作为 "伪装的" private 变量。
#     并不是一种惯例, 它对解释器有特定含义: Python会改写这些名称，以免与子类中定义的名称产生冲突。
#     实际上python并不存在真正的私有变量(仅仅是隐式在类外改名字罢了):
#     双下划线开头的命名形式在 Python 的类成员中使用表示名字改编 (Name Mangling)，即如果有一 Test 类里有一成员 __x，那么 dir(Test) 时会看到 _Test__x 而非 __x。这是为了避免该成员的名称与子类中的名称冲突。但要注意这要求该名称末尾没有下划线。
#     在类外通过_Test__x依然可以访问该变量__x
#     子类无法覆盖父类的__x, 只会定义一个自己的 _子类名__x
#     这种特定的行为差不多等价于Java中的final方法和C++中的正常方法（非虚方法）
#     __x 在子类中需要通过 __父类名_x 来访问
# 
#     单下划线开头还有一种一般不会用到的情况在于使用一个 C 编写的扩展库有时会用下划线开头命名，然后使用一个去掉下划线的 Python 模块进行包装。如 struct 这个模块实际上是 C 模块 _struct 的一个 Python 包装
# 
#     双下划线前缀结尾 __x__
#     双下划线开头双下划线结尾的是一些 Python 的特殊对象，仅仅是一种惯例, 可以被直接引用，但是有特殊用途. 
#     是一种确保Python系统中的名称不会跟用户自定义的名称发生冲突的方式
#     如类成员的 __init__、__del__、__add__、__getitem__ 等，以及全局的 __file__、__name__ 等。 
#     Python 官方推荐永远不要将这样的命名方式应用于自己的变量或函数，而是按照文档说明来使用。
# 
#     单下划线结尾 x_
#     单下划线结尾的样式，这在解析时并没有特别的含义，但通常用于和 Python 关键词区分开来，比如如果我们需要一个变量叫做 class，但 class 是 Python 的关键词，就可以以单下划线结尾写作 class_
#     _
#     解释器中 _ 符号是指交互解释器中最后一次执行语句的返回结果   if _ else ':('
#     _ 还可用作被丢弃的名称 n = 42; for _ in range(n): do_something()
#     _ 还可以被用作函数名
# 
#     单下划线仅是惯例意义上的protected(或private)的原因:
#     Language designers such as Python's Guido van Rossum, in contrast, assume that programmers are responsible adults and capable of good judgment (perhaps not always, but typically). They find that everybody should be able to access the elements of a program if there is a need to do that, so that the language does not get in the way of doing the right thing. (The only programming language that can successfully get in the way of doing the wrong thing is the NULL language)
#     Therefore, _myfield in Python means something like "The designer of this module is doing some non-obvious stuff with this attribute, so please do not modify it and stay away from even reading it if you can -- suitable ways to access relevant information have been provided."
#     [Python “protected” attributes](http://stackoverflow.com/questions/797771/python-protected-attributes)