# -*-coding:utf-8-*-
'''
Created on 2017年5月11日

@author: ghou
'''
import functools
import datetime


# 装饰器
def now1():
    print('2015-3-25')
    
f = now1
# 函数对象有一个__name__属性，可以拿到函数的名字：
print now1.__name__, f.__name__
# 现在，假设我们要增强now()函数的功能，比如，在函数调用前后自动打印日志，但又不希望修改now()函数的定义，这种在代码运行期间动态增加功能的方式，称之为“装饰器”（Decorator）。
# 本质上，decorator就是一个返回函数的高阶函数。所以，我们要定义一个能打印日志的decorator，可以定义如下：
def log(func):
    def wrapper(*args, **kw):
        print('call %s():' % func.__name__)
        return func(*args, **kw)
    return wrapper

# 把@log放到now()函数的定义处，相当于执行了语句：?
# now = log(now)
# 由于log()是一个decorator，返回一个函数，所以，原来的now()函数仍然存在，只是现在同名的now变量指向了新的函数，于是调用now()将执行新函数，即在log()函数中返回的wrapper()函数。
# wrapper()函数的参数定义是(*args, **kw)，因此，wrapper()函数可以接受任意参数的调用。在wrapper()函数内，首先打印日志，再紧接着调用原始函数。
@log
def now():
    print('2015-3-25')

# 观察上面的log，因为它是一个decorator，所以接受一个函数作为参数，并返回一个函数。我们要借助Python的@语法，把decorator置于函数的定义处：
# 调用now()函数，不仅会运行now()函数本身，还会在运行now()函数前打印一行日志：
now()

# 如果decorator本身需要传入参数，那就需要编写一个返回decorator的高阶函数，写出来会更复杂。比如，要自定义log的文本：
def log1(text):
    def decorator(func):
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator

# 这个3层嵌套的decorator用法如下：
@log1('execute')
def now2():
    print('2015-3-25')
now2()

# 和两层嵌套的decorator相比，3层嵌套的效果是这样的：
now2 = log1('ni cai ne')(now2)
now2()
# 我们来剖析上面的语句，首先执行log('execute')，返回的是decorator函数，再调用返回的函数，参数是now函数，返回值最终是wrapper函数。
# 以上两种decorator的定义都没有问题，但还差最后一步。因为我们讲了函数也是对象，它有__name__等属性，但你去看经过decorator装饰之后的函数，它们的__name__已经从原来的'now'变成了'wrapper'：
print now2.__name__
# 因为返回的那个wrapper()函数名字就是'wrapper'，所以，需要把原始函数的__name__等属性复制到wrapper()函数中，否则，有些依赖函数签名的代码执行就会出错。
# 不需要编写wrapper.__name__ = func.__name__这样的代码，Python内置的functools.wraps就是干这个事的，所以，一个完整的decorator的写法如下：
def log2(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        print('call %s():' % func.__name__)
        return func(*args, **kw)
    return wrapper

# 或者针对带参数的decorator：
def log3(text):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            print('%s %s():' % (text, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator
# import functools是导入functools模块。模块的概念稍候讲解。现在，只需记住在定义wrapper()的前面加上@functools.wraps(func)即可。



def log4(text = 'call'):
    def decorator (func):
        @functools.wraps(func)
        def wrapper(*arg, **kw):
            print('%s: %s ' %(text, func.__name__))
            func(*arg, **kw)
            print('end %s' %func.__name__)
            return
        return wrapper
    return decorator
@log4('excute')
def now4():
    print(datetime.datetime.now())




# 文章先由stackoverflow上面的一个问题引起吧，如果使用如下的代码：
# @makebold
# @makeitalic
# def say():
#    return "Hello"
# 
# 打印出如下的输出：
# <b><i>Hello<i></b>
# 
# 你会怎么做？最后给出的答案是：
 
def makebold(fn):
    def wrapped():
        return "<b>" + fn() + "</b>"
    return wrapped
  
def makeitalic(fn):
    def wrapped():
        return "<i>" + fn() + "</i>"
    return wrapped
  
@makebold
@makeitalic
def hello():
    return "hello world"
 
print hello() ## 返回 <b><i>hello world</i></b>
 
 
 
 
# 现在我们来看看如何从一些最基础的方式来理解Python的装饰器。英文讨论参考Here。
# 装饰器是一个很著名的设计模式，经常被用于有切面需求的场景，较为经典的有插入日志、性能测试、事务处理等。装饰器是解决这类问题的绝佳设计，有了装饰器，我们就可以抽离出大量函数中与函数功能本身无关的雷同代码并继续重用。概括的讲，装饰器的作用就是为已经存在的对象添加额外的功能。
# 1.1. 需求是怎么来的？
# 装饰器的定义很是抽象，我们来看一个小例子。
# 
# def foo():
#     print 'in foo()'
# foo()
# 
# 这是一个很无聊的函数没错。但是突然有一个更无聊的人，我们称呼他为B君，说我想看看执行这个函数用了多长时间，好吧，那么我们可以这样做：
# 
# import time
# def foo():
#     start = time.clock()
#     print 'in foo()'
#     end = time.clock()
#     print 'used:', end - start
#  
# foo()
# 
# 很好，功能看起来无懈可击。可是蛋疼的B君此刻突然不想看这个函数了，他对另一个叫foo2的函数产生了更浓厚的兴趣。
# 
# 怎么办呢？如果把以上新增加的代码复制到foo2里，这就犯了大忌了~复制什么的难道不是最讨厌了么！而且，如果B君继续看了其他的函数呢？
# 1.2. 以不变应万变，是变也
# 
# 还记得吗，函数在Python中是一等公民，那么我们可以考虑重新定义一个函数timeit，将foo的引用传递给他，然后在timeit中调用foo并进行计时，这样，我们就达到了不改动foo定义的目的，而且，不论B君看了多少个函数，我们都不用去修改函数定义了！
# 
# import time
#  
# def foo():
#     print 'in foo()'
#  
# def timeit(func):
#     start = time.clock()
#     func()
#     end =time.clock()
#     print 'used:', end - start
#  
# timeit(foo)
# 
# 看起来逻辑上并没有问题，一切都很美好并且运作正常！……等等，我们似乎修改了调用部分的代码。原本我们是这样调用的：foo()，修改以后变成了：timeit(foo)。这样的话，如果foo在N处都被调用了，你就不得不去修改这N处的代码。或者更极端的，考虑其中某处调用的代码无法修改这个情况，比如：这个函数是你交给别人使用的。
# 1.3. 最大限度地少改动！
# 
# 既然如此，我们就来想想办法不修改调用的代码；如果不修改调用代码，也就意味着调用foo()需要产生调用timeit(foo)的效果。我们可以想到将timeit赋值给foo，但是timeit似乎带有一个参数……想办法把参数统一吧！如果timeit(foo)不是直接产生调用效果，而是返回一个与foo参数列表一致的函数的话……就很好办了，将timeit(foo)的返回值赋值给foo，然后，调用foo()的代码完全不用修改！
# 
# #-*- coding: UTF-8 -*-
# import time
#  
# def foo():
#     print 'in foo()'
#  
# # 定义一个计时器，传入一个，并返回另一个附加了计时功能的方法
# def timeit(func):
#      
#     # 定义一个内嵌的包装函数，给传入的函数加上计时功能的包装
#     def wrapper():
#         start = time.clock()
#         func()
#         end =time.clock()
#         print 'used:', end - start
#      
#     # 将包装后的函数返回
#     return wrapper
#  
# foo = timeit(foo)
# foo()
# 
# 这样，一个简易的计时器就做好了！我们只需要在定义foo以后调用foo之前，加上foo = timeit(foo)，就可以达到计时的目的，这也就是装饰器的概念，看起来像是foo被timeit装饰了。在在这个例子中，函数进入和退出时需要计时，这被称为一个横切面(Aspect)，这种编程方式被称为面向切面的编程(Aspect-Oriented Programming)。与传统编程习惯的从上往下执行方式相比较而言，像是在函数执行的流程中横向地插入了一段逻辑。在特定的业务领域里，能减少大量重复代码。面向切面编程还有相当多的术语，这里就不多做介绍，感兴趣的话可以去找找相关的资料。
# 
# 这个例子仅用于演示，并没有考虑foo带有参数和有返回值的情况，完善它的重任就交给你了 ：）
# 
# 上面这段代码看起来似乎已经不能再精简了，Python于是提供了一个语法糖来降低字符输入量。
# 
# import time
#  
# def timeit(func):
#     def wrapper():
#         start = time.clock()
#         func()
#         end =time.clock()
#         print 'used:', end - start
#     return wrapper
#  
# @timeit
# def foo():
#     print 'in foo()'
#  
# foo()
# 
# 重点关注第11行的@timeit，在定义上加上这一行与另外写foo = timeit(foo)完全等价，千万不要以为@有另外的魔力。除了字符输入少了一些，还有一个额外的好处：这样看上去更有装饰器的感觉。
# 
# -------------------
# 
# 要理解python的装饰器，我们首先必须明白在Python中函数也是被视为对象。这一点很重要。先看一个例子：
# 
# def shout(word="yes") :
#     return word.capitalize()+" !"
#  
# print shout()
# # 输出 : 'Yes !'
#  
# # 作为一个对象，你可以把函数赋给任何其他对象变量 
#  
# scream = shout
#  
# # 注意我们没有使用圆括号，因为我们不是在调用函数
# # 我们把函数shout赋给scream，也就是说你可以通过scream调用shout
#  
# print scream()
# # 输出 : 'Yes !'
#  
# # 还有，你可以删除旧的名字shout，但是你仍然可以通过scream来访问该函数
#  
# del shout
# try :
#     print shout()
# except NameError, e :
#     print e
#     #输出 : "name 'shout' is not defined"
#  
# print scream()
# # 输出 : 'Yes !'
# 
# 我们暂且把这个话题放旁边，我们先看看python另外一个很有意思的属性：可以在函数中定义函数：
# 
# def talk() :
#  
#     # 你可以在talk中定义另外一个函数
#     def whisper(word="yes") :
#         return word.lower()+"...";
#  
#     # ... 并且立马使用它
#  
#     print whisper()
#  
# # 你每次调用'talk'，定义在talk里面的whisper同样也会被调用
# talk()
# # 输出 :
# # yes...
#  
# # 但是"whisper" 不会单独存在:
#  
# try :
#     print whisper()
# except NameError, e :
#     print e
#     #输出 : "name 'whisper' is not defined"*
# 
# 函数引用
# 
# 从以上两个例子我们可以得出，函数既然作为一个对象，因此：
# 
# 1. 其可以被赋给其他变量
# 
# 2. 其可以被定义在另外一个函数内
# 
# 这也就是说，函数可以返回一个函数，看下面的例子：
# 
# def getTalk(type="shout") :
#  
#     # 我们定义另外一个函数
#     def shout(word="yes") :
#         return word.capitalize()+" !"
#  
#     def whisper(word="yes") :
#         return word.lower()+"...";
#  
#     # 然后我们返回其中一个
#     if type == "shout" :
#         # 我们没有使用(),因为我们不是在调用该函数
#         # 我们是在返回该函数
#         return shout
#     else :
#         return whisper
#  
# # 然后怎么使用呢 ?
#  
# # 把该函数赋予某个变量
# talk = getTalk()     
#  
# # 这里你可以看到talk其实是一个函数对象:
# print talk
# #输出 : <function shout at 0xb7ea817c>
#  
# # 该对象由函数返回的其中一个对象:
# print talk()
#  
# # 或者你可以直接如下调用 :
# print getTalk("whisper")()
# #输出 : yes...
# 
# 还有，既然可以返回一个函数，我们可以把它作为参数传递给函数：
# 
# def doSomethingBefore(func) :
#     print "I do something before then I call the function you gave me"
#     print func()
#  
# doSomethingBefore(scream)
# #输出 :
# #I do something before then I call the function you gave me
# #Yes !
# 
# 这里你已经足够能理解装饰器了，其他它可被视为封装器。也就是说，它能够让你在装饰前后执行代码而无须改变函数本身内容。
# 
# 手工装饰
# 
# 那么如何进行手动装饰呢？
# 
# # 装饰器是一个函数，而其参数为另外一个函数
# def my_shiny_new_decorator(a_function_to_decorate) :
#  
#     # 在内部定义了另外一个函数：一个封装器。
#     # 这个函数将原始函数进行封装，所以你可以在它之前或者之后执行一些代码
#     def the_wrapper_around_the_original_function() :
#  
#         # 放一些你希望在真正函数执行前的一些代码
#         print "Before the function runs"
#  
#         # 执行原始函数
#         a_function_to_decorate()
#  
#         # 放一些你希望在原始函数执行后的一些代码
#         print "After the function runs"
#  
#     #在此刻，"a_function_to_decrorate"还没有被执行，我们返回了创建的封装函数
#     #封装器包含了函数以及其前后执行的代码，其已经准备完毕
#     return the_wrapper_around_the_original_function
#  
# # 现在想象下，你创建了一个你永远也不远再次接触的函数
# def a_stand_alone_function() :
#     print "I am a stand alone function, don't you dare modify me"
#  
# a_stand_alone_function()
# #输出: I am a stand alone function, don't you dare modify me
#  
# # 好了，你可以封装它实现行为的扩展。可以简单的把它丢给装饰器
# # 装饰器将动态地把它和你要的代码封装起来，并且返回一个新的可用的函数。
# a_stand_alone_function_decorated = my_shiny_new_decorator(a_stand_alone_function)
# a_stand_alone_function_decorated()
# #输出 :
# #Before the function runs
# #I am a stand alone function, don't you dare modify me
# #After the function runs
# 
# 现在你也许要求当每次调用a_stand_alone_function时，实际调用却是a_stand_alone_function_decorated。实现也很简单，可以用my_shiny_new_decorator来给a_stand_alone_function重新赋值。
# 
# a_stand_alone_function = my_shiny_new_decorator(a_stand_alone_function)
# a_stand_alone_function()
# #输出 :
# #Before the function runs
# #I am a stand alone function, don't you dare modify me
# #After the function runs
#  
# # And guess what, that's EXACTLY what decorators do !
# 
# 装饰器揭秘
# 
# 前面的例子，我们可以使用装饰器的语法：
# 
# @my_shiny_new_decorator
# def another_stand_alone_function() :
#     print "Leave me alone"
#  
# another_stand_alone_function()
# #输出 :
# #Before the function runs
# #Leave me alone
# #After the function runs
# 
# 当然你也可以累积装饰：
# 
# def bread(func) :
#     def wrapper() :
#         print "</''''''\>"
#         func()
#         print "<\______/>"
#     return wrapper
#  
# def ingredients(func) :
#     def wrapper() :
#         print "#tomatoes#"
#         func()
#         print "~salad~"
#     return wrapper
#  
# def sandwich(food="--ham--") :
#     print food
#  
# sandwich()
# #输出 : --ham--
# sandwich = bread(ingredients(sandwich))
# sandwich()
# #outputs :
# #</''''''\>
# # #tomatoes#
# # --ham--
# # ~salad~
# #<\______/>
# 
# 使用python装饰器语法：
# 
# @bread
# @ingredients
# def sandwich(food="--ham--") :
#     print food
#  
# sandwich()
# #输出 :
# #</''''''\>
# # #tomatoes#
# # --ham--
# # ~salad~
# #<\______/>
# 
# 装饰器的顺序很重要，需要注意：
# 
# @ingredients
# @bread
# def strange_sandwich(food="--ham--") :
#     print food
#  
# strange_sandwich()
# #输出 :
# ##tomatoes#
# #</''''''\>
# # --ham--
# #<\______/>
# # ~salad~
# 
# 最后回答前面提到的问题：
# 
# # 装饰器makebold用于转换为粗体
# def makebold(fn):
#     # 结果返回该函数
#     def wrapper():
#         # 插入一些执行前后的代码
#         return "<b>" + fn() + "</b>"
#     return wrapper
#  
# # 装饰器makeitalic用于转换为斜体
# def makeitalic(fn):
#     # 结果返回该函数
#     def wrapper():
#         # 插入一些执行前后的代码
#         return "<i>" + fn() + "</i>"
#     return wrapper
#  
# @makebold
# @makeitalic
# def say():
#     return "hello"
#  
# print say()
# #输出: <b><i>hello</i></b>
#  
# # 等同于
# def say():
#     return "hello"
# say = makebold(makeitalic(say))
#  
# print say()
# #输出: <b><i>hello</i></b>
# 
# 内置的装饰器
# 
# 内置的装饰器有三个，分别是staticmethod、classmethod和property，作用分别是把类中定义的实例方法变成静态方法、类方法和类属性。由于模块里可以定义函数，所以静态方法和类方法的用处并不是太多，除非你想要完全的面向对象编程。而属性也不是不可或缺的，Java没有属性也一样活得很滋润。从我个人的Python经验来看，我没有使用过property，使用staticmethod和classmethod的频率也非常低。
# 
# class Rabbit(object):
#      
#     def __init__(self, name):
#         self._name = name
#      
#     @staticmethod
#     def newRabbit(name):
#         return Rabbit(name)
#      
#     @classmethod
#     def newRabbit2(cls):
#         return Rabbit('')
#      
#     @property
#     def name(self):
#         return self._name
# 
# 这里定义的属性是一个只读属性，如果需要可写，则需要再定义一个setter：
# 
# @name.setter
# def name(self, name):
#     self._name = name
# 
# functools模块
# 
# functools模块提供了两个装饰器。这个模块是Python 2.5后新增的，一般来说大家用的应该都高于这个版本。但我平时的工作环境是2.4 T-T
# 
# 2.3.1. wraps(wrapped[, assigned][, updated]):
# 这是一个很有用的装饰器。看过前一篇反射的朋友应该知道，函数是有几个特殊属性比如函数名，在被装饰后，上例中的函数名foo会变成包装函数的名字wrapper，如果你希望使用反射，可能会导致意外的结果。这个装饰器可以解决这个问题，它能将装饰过的函数的特殊属性保留。
# 
# import time
# import functools
#  
# def timeit(func):
#     @functools.wraps(func)
#     def wrapper():
#         start = time.clock()
#         func()
#         end =time.clock()
#         print 'used:', end - start
#     return wrapper
#  
# @timeit
# def foo():
#     print 'in foo()'
#  
# foo()
# print foo.__name__
# 
# 首先注意第5行，如果注释这一行，foo.__name__将是'wrapper'。另外相信你也注意到了，这个装饰器竟然带有一个参数。实际上，他还有另外两个可选的参数，assigned中的属性名将使用赋值的方式替换，而updated中的属性名将使用update的方式合并，你可以通过查看functools的源代码获得它们的默认值。对于这个装饰器，相当于wrapper = functools.wraps(func)(wrapper)。
# 
# 2.3.2. total_ordering(cls):
# 这个装饰器在特定的场合有一定用处，但是它是在Python 2.7后新增的。它的作用是为实现了至少__lt__、__le__、__gt__、__ge__其中一个的类加上其他的比较方法，这是一个类装饰器。如果觉得不好理解，不妨仔细看看这个装饰器的源代码：
# 
# def total_ordering(cls):
#     """Class decorator that fills in missing ordering methods"""
#     convert = {
#         '__lt__': [('__gt__', lambda self, other: other < self),
#                  ('__le__', lambda self, other: not other < self),
#                   ('__ge__', lambda self, other: not self < other)],
#         '__le__': [('__ge__', lambda self, other: other <= self),
#                     ('__lt__', lambda self, other: not other <= self),
#                     ('__gt__', lambda self, other: not self <= other)],
#          '__gt__': [('__lt__', lambda self, other: other > self),
#                     ('__ge__', lambda self, other: not other > self),
#                   ('__le__', lambda self, other: not self > other)],
#         '__ge__': [('__le__', lambda self, other: other >= self),
#                     ('__gt__', lambda self, other: not other >= self),
#                      ('__lt__', lambda self, other: not self >= other)]
#     }
#     roots = set(dir(cls)) & set(convert)
#     if not roots:
#         raise ValueError('must define at least one ordering operation: < > <= >=')
#         root = max(roots)       # prefer __lt__ to __le__ to __gt__ to __ge__
#         for opname, opfunc in convert[root]:
#             if opname not in roots:
#             opfunc.__name__ = opname
#             opfunc.__doc__ = getattr(int, opname).__doc__
#             setattr(cls, opname, opfunc)
#     return cls