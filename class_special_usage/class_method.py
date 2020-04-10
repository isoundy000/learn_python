# -*-coding:utf-8-*-
'''
Created on 2017年3月21日

@author: ghou
'''

# Python标准库：内置函数issubclass(class, classinfo)
# 本函数用来判断类参数class是否是类型参数classinfo的子类。
# issubclass()
class Line:
    pass

class RedLine(Line):  
    pass
      
class Rect:  
    pass  
      
print(issubclass(RedLine, Line))  
print(issubclass(Rect, Line))

# 对象的类型
a = 10
print(isinstance(a, (int, str)))


class HouGuangDong(object):

    @classmethod
    def store(cls, xing, age, entities={}):
        print(xing, age, entities)


HouGuangDong.store('hou', 17, {'13': '12'})

# 访问限制
# 如果要让内部属性不被外部访问，可以把属性的名称前加上两个下划线__，在Python中，实例的变量名如果以__开头，就变成了一个私有变量（private），只有内部可以访问，外部不能访问，所以，我们把Student类改一改：
class Student(object):

    def __init__(self, name, score):
        self.__name = name
        self.__score = score
    
    def print_score(self):
        print('%s: %s' % (self.__name, self.__score))
    
    def get_name(self):
        return self.__name
    
    def get_score(self):
        return self.__score
    
    def set_score(self, score):
        if 0 <= score <= 100:
            self.__score = score
        else:
            raise ValueError('bad score')   

 
# 改完后，对于外部代码来说，没什么变动，但是已经无法从外部访问实例变量.__name和实例变量.__score了：
bart = Student("ghou", 99)
print(bart._Student__name)
print(bart.__name)
# 这样就确保了外部代码不能随意修改对象内部的状态，这样通过访问限制的保护，代码更加健壮。
# 但是如果外部代码要获取name和score怎么办？可以给Student类增加get_name和get_score这样的方法：
# 如果又要允许外部代码修改score怎么办？可以给Student类增加set_score方法：
# 你也许会问，原先那种直接通过bart.score = 59也可以修改啊，为什么要定义一个方法大费周折？因为在方法中，可以对参数做检查，避免传入无效的参数：
# 需要注意的是，在Python中，变量名类似__xxx__的，也就是以双下划线开头，并且以双下划线结尾的，是特殊变量，特殊变量是可以直接访问的，不是private变量，所以，不能用__name__、__score__这样的变量名。
# 有些时候，你会看到以一个下划线开头的实例变量名，比如_name，这样的实例变量外部是可以访问的，但是，按照约定俗成的规定，当你看到这样的变量时，意思就是，“虽然我可以被访问，但是，请把我视为私有变量，不要随意访问”。
# 双下划线开头的实例变量是不是一定不能从外部访问呢？其实也不是。不能直接访问__name是因为Python解释器对外把__name变量改成了_Student__name，所以，仍然可以通过_Student__name来访问__name变量：