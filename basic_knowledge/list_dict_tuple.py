# -*- encoding: utf-8 -*-
'''
Created on 2017年8月2日

@author: houguangdong
'''
# python的list,dict,tuple比较和应用
# python提供了好多的数据结构，主要是分list,dict,tuple（数组，字典，元组）
# 1.list（数组）
# 数组的方法运用，应该有写过程序的都知道啦
# 包括二维三维，下面我只说几个方法
# x代表数组中的元素，i代表位置
# a) append(x) 把元素x添加到数组的尾部
# b) insert(i,x) 把元素x 插入到位置i
# c) remove(x) 删除第一个元素x
# d) pop(i) 删除第i个元素，并返回这个元素。若调用pop()则删除最后一个元素
# e) index(x) 返回数组中第一个值为x的位置。如果没有匹配的元素会抛出一个错误
# f) count(x) 返回x在数组中出现的次数
# g) sort() 对数组中的元素进行排序
# h) reverse() 对数组中的元素用倒序排序
# 2.dict（字典）
# 这一个有必要说多一些东西，因为比较好用，而且在别的语言里也较少
# 字典（Dictionary）是一种映射结构的数据类型，由无序的“键－值对”组成。字典的键必须是不可改变的类型，如：字符串，数字，tuple；值可以为任何python数据类型。
# 1)、新建字典
# dict1={}      #建立一个空字典
# type(dict1)
# <type ‘dict’>
# 2)、增加字典元素：两种方法
# dict1['a']=1    #第一种
# dict1
# {’a': 1}
# #第二种：setdefault方法
# dict1.setdefault(’b',2)
# 2
# dict1
# {’a': 1, ‘b’: 2}
# 3)、删除字典
# #删除指定键－值对
# dict1
# {’a': 1, ‘b’: 2}
# del dict1['a']      #也可以用pop方法，dict1.pop(’a')
# dict1
# {’b': 2}
# #清空字典
# dict1.clear()
# dict1         #字典变为空了
# {}
# #删除字典对象
# del dict1
# 4)、字典的方法
# 1)get(key,default=None)
# 返回键值key对应的值；如果key没有在字典里，则返回default参数的值，默认为None
# dict1         #空的字典
# {}
# dict1.get(’a')   #键‘a’在dict1中不存在，返回none
# dict1.get(’d1′,’no1′)   #default参数给出值’no1′，所以返回’no1′
# ‘no1′
# dict1['a']=’no1′      #插入一个新元素
# dict1
# {’a': ‘1111′}
# dict1.get(’a')      #现在键’a'存在，返回其值
# ‘1111′
# (2)clear
# 清空字典
# (3)has_key(key)
# 如果key出现在dict里则返回True；否则返回False
# dict1
# {’a': ‘1111′}
# dict1.has_key(’b')
# False
# dict1.has_key(’a')
# True
# (4)items
# 返回dict的（键，值）tuple对的一个列表
# dict1
# {’a': ‘no1′, ‘b’: ‘2222′}
# dict1.items()
# [('a', 'no1'), ('b', '2222')]
# (5)keys   返回dict的键列表
# (6)values 返回dict的值列表
# dict1
# {’a': ‘no1′, ‘b’: ‘2222′}
# dict1.keys()
# ['a', 'b']
# dict1.values()
# ['no1', '2222']
# (7)setdefault(key,default=None)
# 如果dict中有key，则返回key值，如果没有找到key，则在dict中加上该key，值由default参数给出，默认None
# (8)update(dict2)
# 把dict2的元素加入到dict中去，键字重复时会覆盖dict中的键值
# dict2
# {’c': ‘3333′, ‘b’: ‘no2′}
# dict1                  #dict2和dict1的键‘b’重复
# {’a': ‘no1′, ‘b’: ‘2222′}
# dict1.update(dict2)     #调用update后，dict1的键’b'值被覆盖了
# dict1
# {’a': ‘no1′, ‘c’: ‘3333′, ‘b’: ‘no2′}
# (9)popitem
# 删除任意键－值对，并返回该键－值对，如字典为空，则产生异常
# dict1
# {’b': ‘no2′}
# dict1.popitem()
# (’b', ‘no2′)
# dict1
# {}
# dict1.popitem()
# Traceback (most recent call last):
# File “<interactive input>”, line 1, in <module>
# KeyError: ‘popitem(): dictionary is empty’
# (10)pop(key,[d])
# 删除指定键字的键－值对，并返回该键对应的值   ＃第二个参数不知道怎么用
# dict1
# {’a': ‘no1′, ‘c’: ‘3333′, ‘b’: ‘no2′}
# dict1.pop(’a')
# ‘no1′
# dict1
# {’c': ‘3333′, ‘b’: ‘no2′}
# (11)copy
# 返回字典的一个浅拷贝
# #以下方法目前还不知道怎么用
# (12)fromkeys
# (13)iteritems
# (14)iterkeys
# (15)itervalues
# 3.tuple(元组)
# tuple是python中一个相对简单的类型，它的特点是：有顺序的、不可变的。因此，很显然地tuple有像list 和string一样的 indexing和slicing（分片）的功能，可以通过标号对成员进行访问。同时由于tuple是不可变的，因此试图改变tuple成员的是非法的。 不过由于tuple中的成员可以是list，而list是可变的，因此改变tuple成员的成员是可行的。这怎么理解呢？tuple中保存的中是各个成员 的指针，所说的tuple不可变，也就是说指向各个成员的地址是不可变的。更改作为tuple成员的list里的成员，并不需要变更在tuple中指向这 个list的指针，因此tuple并没有改变。
# 内置函数tuple([seq])用于把seq转换成tuple。此外，与list和string不同，tuple没有专属的函数。
# tuple的表示形式如下：
#     （成员1, 成员2…）
# 考虑只有一个成员的例子，(成员1)，由于小括号也用于表达式的分组，这就会产生一个问题，当你写下了：
#     T=(23)
# 这一行代码的时候，python怎么知道你是要把23这个整数赋予T呢，还是要把只有一个成员的tuple给T呢。所以，python规定，这种形式表示把T赋为整数23。而只有一个成员的tuple应该用如下的方式表示：
#     T=（23,）
# 即在唯一的成员后面加上一个逗号。
# 4.总结一下：
# list是顺序的，可变的。
# dictrionary是无顺序的，可变的
# tuple是顺序的，不可变的。
# 三者最好是结合起来用，个有个的优点，例如：
# a=((1,”abc”),(2,”efg”),(3,”ghi”))
# 如果我选择1的话，如何返回abc
# a=((1,"abc"),(2,"efg"),(3,"ghi"))
# dict(a)[1]
# 'abc'


# 元祖 Tuple
# 特点：元祖内的数据不可变
# 一个元素的定义：T = （1，）
# T=(1,)
# type(T)
# <type 'tuple'>
# 特殊的元祖：”可变”的元祖
# T=(1,2,3,[1,2,3])
# T[3][2] = 'vimiix'
# T
# (1, 2, 3, [1, 2, 'vimiix'])
# 看上去元祖发生了变化，但真正变化的是[1，2，3]这个列表内的元素发生了变化，但是这个列表在T这个元祖中的内存地址是没有改变的。
# 结论：实际是元祖的元素包含了可变的元素，但是元祖中元素的内存地址没有变，所以所谓的元祖不可变是指元素指向的内存地址是不变
# 字典 Dict
# 特点：
#       1、字典是Python中唯一的映射类型
#       2、字典的键（KEY）必须是不可变的对象—>因为字典在计算机中是通过Hash算法存储的，Hash的特点是由KEY来计算存储的，如果KEY可变，将会导致数据混乱。
# D = {1:3,'vimiix':88}
# type(D)
# <type 'dict'>
# D={[1,2,3]:100}
# Traceback (most recent call last):
#  File "<pyshell#15>", line 1, in <module>
#  D={[1,2,3]:100}
# TypeError: unhashable type: 'list' (这里提示list是不能被Hash计算的数据类型，因为list是可变的数据类型)
# 由此错误可以看出，字典的键只能使用不可变的对象（元祖是可以的），但是对于字典的值没有此要求
# 键值对用冒号‘：'分割，每个对之间用逗号‘，'分开，所有这些用花括号‘{}'包含起来
# 字典中的键值对是没有顺序的，故不可以用索引访问，只可以通过键取得所对应的值
# 拓展：如果定义的过程中，出现相同的键，最后存储的时候回保留最后的一个键值对）
# D= {1:2,1:3}
# D
# {1: 3}
# 创建与访问
# 第一种创建方式：直接通过花括号包含键值对来创建
# 第二种创建方式：利用内置函数dict()来创建，注意！dict（）括号内只能有一个参数，要把所有的键值对括起来
# （1）
# D =dict((1,2),(3,4),(5,6))
# Traceback (most recent call last):
#  File "<pyshell#20>", line 1, in <module>
#  D =dict((1,2),(3,4),(5,6))
# TypeError: dict expected at most 1 arguments, got 3
# D =dict(((1,2),(3,4),(5,6)))
# D
# {1: 2, 3: 4, 5: 6}
# （2）还可以指定关键字参数
# D=dict(vimiix = 'VIMIIX')
# D
# {'vimiix': 'VIMIIX'}
# 这里的小写‘vimiix'不可以加单引号，加了会报错！
# （3）dict的内置方法 .fromkeys 有两个参数
# D = dict.fromkeys((1,'vimiix'),('common','value'))
# D
# {1: ('common', 'value'), 'vimiix': ('common', 'value')}
# 实际的生产过程中，都是使用字典生成式来创建，根据现有的数据来生成对应的数据，有数据才有意义。
# 字典生成式栗子：
# L1 = [1,2,3]
# L2 = ['a','v','vimiix']
# D={a:b for a in L1 for b in L2}
# D
# {1: 'vimiix', 2: 'vimiix', 3: 'vimiix'}
# 此处只是一个生成式的栗子，但并不是理想答案，待学习如何生成一一对应的键值对
# 字典的内置方法：
# get() :
# 获取键所对应的值，如果未找到返回None，找到返回对应的值
# pop(key) :
# 弹出key对应的值，默认最后一个
# popitem() :
# 随机返回并删除字典中的一对键和值（项）。为什么是随机删除呢？因为字典是无序的，没有所谓的“最后一项”或是其它顺序。在工作时如果遇到需要逐一删除项的工作，用popitem()方法效率很高。
# update() :
# 更新或者新增一个键值对（有则改之无则加勉）
# D.update({'newitem':'update'})
# D
# {'newitem': 'update', 1: 'vimiix', 2: 'vimiix', 3: 'vimiix'}

#  Python中 dict.items() dict.iteritems()区别 
# dict.items()返回的是一个完整的列表，而dict.iteritems()返回的是一个生成器(迭代器)。
# dict.items()返回列表list的所有列表项，形如这样的二元组list：［(key,value),(key,value),...］,dict.iteritems()是generator, yield 2-tuple。相对来说，前者需要花费更多内存空间和时间，但访问某一项的时间较快(KEY)。后者花费很少的空间，通过next()不断取下一个值，但是将花费稍微多的时间来生成下一item。