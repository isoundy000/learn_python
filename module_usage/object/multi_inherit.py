#!/usr/bin/env python
# -*-encoding:utf-8-*-
'''
Created on 2017年7月30日

@author: houguangdong
'''

class Animal(object):
    pass


# 大类
class Mammal(Animal):
    pass


class Bird(Animal):
    pass


# 各种动物：
class Dog(Mammal):
    pass


class Bat(Mammal):
    pass


class Parrot(Bird):
    pass


class Ostrich(Bird):
    pass

# 现在，我们要给动物再加上Runnable和Flyable的功能，只需要先定义好Runnable和Flyable的类：
class Runnable(object):
    def run(self):
        print 'Running...'
        
        
class Flyable(object):
    def fly(self):
        print 'Flying...'
        
# 对于需要Runnable功能的动物，就多继承一个Runnable，例如Dog：
class Dog1(Mammal, Runnable):
    pass


# 对于需要Flyable功能的动物，就多继承一个Flyable，例如Bat：
class Bat1(Mammal, Flyable):
    pass

# 通过多重继承，一个子类就可以同时获得多个父类的所有功能。

# Mixin
# 在设计类的继承关系时，通常，主线都是单一继承下来的，例如，Ostrich继承自Bird。但是，如果需要“混入”额外的功能，通过多重继承就可以实现，比如，让Ostrich除了继承自Bird外，再同时继承Runnable。这种设计通常称之为Mixin。
# 为了更好地看出继承关系，我们把Runnable和Flyable改为RunnableMixin和FlyableMixin。类似的，你还可以定义出肉食动物CarnivorousMixin和植食动物HerbivoresMixin，让某个动物同时拥有好几个Mixin：
# class Dog2(Mammal, Runnable, CarnivorousMixin):

# Mixin的目的就是给一个类增加多个功能，这样，在设计类的时候，我们优先考虑通过多重继承来组合多个Mixin的功能，而不是设计多层次的复杂的继承关系。
# Python自带的很多库也使用了Mixin。举个例子，Python自带了TCPServer和UDPServer这两类网络服务，而要同时服务多个用户就必须使用多进程或多线程模型，这两种模型由ForkingMixin和ThreadingMixin提供。通过组合，我们就可以创造出合适的服务来。
# 比如，编写一个多进程模式的TCP服务，定义如下：
# class MyTCPServer(TCPServer, ForkingMixin):
#     pass
# 编写一个多线程模式的UDP服务，定义如下：
# class MyUDPServer(UDPServer, ThreadingMixin):
#     pass
# 如果你打算搞一个更先进的协程模型，可以编写一个CoroutineMixin：
# class MyTCPServer(TCPServer, CoroutineMixin):
#     pass
# 这样一来，我们不需要复杂而庞大的继承链，只要选择组合不同的类的功能，就可以快速构造出所需的子类。
# 小结
# 由于Python允许使用多重继承，因此，Mixin就是一种常见的设计。
# 只允许单一继承的语言（如Java）不能使用Mixin的设计。

class Grandfa(object):
    def hair(self):
        pass

class Father(Grandfa):
    pass

class Mom(object):
    def hair(self):
        print 'hair'

class Tom(Father, Mom):
    pass

me=Tom()
me.hair()
# 试了下，继承谁在前就执行谁的方法，如果没有则不执行；
# 深度继承，如果子类有方法执行自己的方法，如果子类没有父类有则执行父类的方法；
# 如果否继承自Object,第一个没有方法执行第二个，第一个有限原则
# 经典类和新式类的继承方向不同 继承搜索的顺序发生了改变,经典类多继承属性搜索顺序: 先深入继承树左侧，再返回，开始找右侧;新式类多继承属性搜索顺序: 先水平搜索，然后再向上移动
