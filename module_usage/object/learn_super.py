#!/usr/bin/env python
# -*-encoding:utf-8-*-
'''
Created on 2017年8月1日

@author: houguangdong
'''

# Python中super()方法的使用
# 如果在子类中也定义了构造器，既_init_()函数，那么基类的构造器该如何调用呢？
# 方法一、明确指定
# 使用一个子类的实例去调用基类的构造器，在子类的构造器中明确的指明调用基类的构造器。
class P(object):
    def __init__(self):
        print 'p is call'

class C(P):
    def __init__(self):
        P.__init__(self)
        print 'calling Cs construtor'
C()

# 方法二、使用super()方法
# super()方法的漂亮之处在于，你不需要在定义子类构造器时，明确的指定子类的基类并显式的调用，即不需要明确的提供父类，这样做的好处就是，如果你改变了继承的父类，你只需要修改一行代码（class代码行），而不需要在大量代码中去查找那个要修改的基类。另外一方面代码的可移植性和重用性也更高。
class C1(P):
    def __init__(self):
        super(C1, self).__init__()
        print 'calling Cs1 construtor'

c = C1()

# super 是用来解决多重继承问题的，直接用类名调用父类方法在使用单继承的时候没问题，但是如果使用多继承，会涉及到查找顺序（MRO）、重复调用（钻石继承）等种种问题。总之前人留下的经验就是：保持一致性。要不全部用类名调用父类，要不就全部用 super，不要一半一半。
# class FooParent(object):
#     def __init__(self):
#         self.parent = 'I\'m the parent.'
#         print 'Parent'
#     
#     def bar(self,message):
#         print message, 'from Parent'
#         
# class FooChild(FooParent):
#     def __init__(self):
#         FooParent.__init__(self)
#         print 'Child'
#         
#     def bar(self,message):
#         FooParent.bar(self,message)
#         print 'Child bar function.'
#         print self.parent


class FooParent(object):
    def __init__(self):
        self.parent = 'I\'m the parent.'
        print 'Parent'
    
    def bar(self,message):
        print message,'from Parent'

class FooChild(FooParent):
    def __init__(self):
        super(FooChild,self).__init__()
        print 'Child'
        
    def bar(self,message):
        super(FooChild, self).bar(message)
        print 'Child bar fuction'
        print self.parent

# 在我们的印象中，对于super(B, self).__init__()是这样理解的：super(B, self)首先找到B的父类（就是类A），然后把类B的对象self转换为类A的对象（通过某种方式，一直没有考究是什么方式，惭愧），然后“被转换”的类A对象调用自己的__init__函数。考虑到super中只有指明子类的机制，因此，在多继承的类定义中，通常我们保留使用类似代码段1的方法。
        
if __name__=='__main__':
    fooChild = FooChild()
    fooChild.bar('HelloWorld')
    
# 从运行结果上看，普通继承和super继承是一样的。但是其实它们的内部运行机制不一样，这一点在多重继承时体现得很明显。在super机制里可以保证公共父类仅被执行一次，至于执行的顺序，是按照mro进行的（E.__mro__）。
# 注意：super继承只能用于新式类，用于经典类时就会报错。
# 新式类：必须有继承的类，如果没什么想继承的，那就继承object
# 经典类：没有父类，如果此时调用super就会出现错误：『super() argument 1 must be type, not classobj』
# 更详细的参考
# http://blog.csdn.net/johnsonguo/article/details/585193
# 总结
# 　　1. super并不是一个函数，是一个类名，形如super(B, self)事实上调用了super类的初始化函数，
#        产生了一个super对象；
# 　　2. super类的初始化函数并没有做什么特殊的操作，只是简单记录了类类型和具体实例；
# 　　3. super(B, self).func的调用并不是用于调用当前类的父类的func函数；
# 　　4. Python的多继承类是通过mro的方式来保证各个父类的函数被逐一调用，而且保证每个父类函数
#        只调用一次（如果每个类都使用super）；
# 　　5. 混用super类和非绑定的函数是一个危险行为，这可能导致应该调用的父类函数没有调用或者一
#        个父类函数被调用多次。

#  代码段9：
# 
#  class A(object):
#   def __init__(self):
#    print "enter A"
#    super(A, self).__init__()  # new
#    print "leave A"
# 
#  class B(object):
#   def __init__(self):
#    print "enter B"
#    super(B, self).__init__()  # new
#    print "leave B"
# 
#  class C(A):
#   def __init__(self):
#    print "enter C"
#    super(C, self).__init__()
#    print "leave C"
# 
#  class D(A):
#   def __init__(self):
#    print "enter D"
#    super(D, self).__init__()
#    print "leave D"
#  class E(B, C):
#   def __init__(self):
#    print "enter E"
#    super(E, self).__init__()  # change
#    print "leave E"
# 
#  class F(E, D):
#   def __init__(self):
#    print "enter F"
#    super(F, self).__init__()  # change
#    print "leave F"
# 
#  >>> f = F()
#  
# 
# 代码段4：
# 
#  class A(object):
#   def __init__(self):
#    print "enter A"
#    print "leave A"
# 
#  class B(object):
#   def __init__(self):
#    print "enter B"
#    print "leave B"
# 
#  class C(A):
#   def __init__(self):
#    print "enter C"
#    super(C, self).__init__()
#    print "leave C"
# 
#  class D(A):
#   def __init__(self):
#    print "enter D"
#    super(D, self).__init__()
#    print "leave D"
#  class E(B, C):
#   def __init__(self):
#    print "enter E"
#    B.__init__(self)
#    C.__init__(self)
#    print "leave E"
# 
#  class F(E, D):
#   def __init__(self):
#    print "enter F"
#    E.__init__(self)
#    D.__init__(self)
#    print "leave F"
# 
#  >>> f = F()