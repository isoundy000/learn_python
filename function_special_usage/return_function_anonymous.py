# -*- encoding: utf-8 -*-
'''
Created on 7/27/2017

@author: houguangdong
'''

# 返回函数 函数作为返回值
# 如果不需要立刻求和，而是在后面的代码中，根据需要再计算怎么办？可以不返回求和的结果，而是返回求和的函数！
def lazy_sum(*args):
    def sum():
        ax = 0
        for n in args:
            ax = ax + n
        return ax
    return sum

# 当我们调用lazy_sum()时，返回的并不是求和结果，而是求和函数：
f = lazy_sum(1, 3, 5, 7, 9)
print f()

# 在这个例子中，我们在函数lazy_sum中又定义了函数sum，并且，内部函数sum可以引用外部函数lazy_sum的参数和局部变量，当lazy_sum返回函数sum时，相关参数和变量都保存在返回的函数中，这种称为“闭包（Closure）”的程序结构拥有极大的威力。
# 请再注意一点，当我们调用lazy_sum()时，每次调用都会返回一个新的函数，即使传入相同的参数：
f1 = lazy_sum(1, 3, 5, 7, 9)
f2 = lazy_sum(1, 3, 5, 7, 9)
# f1()和f2()的调用结果互不影响。
print f1==f2
# 闭包
# 注意到返回的函数在其定义内部引用了局部变量args，所以，当一个函数返回了一个函数后，其内部的局部变量还被新函数引用，所以，闭包用起来简单，实现起来可不容易。

def count():
    fs = []
    for i in range(1, 4):
        def f():
            return i*i
        fs.append(f)
    return fs
f1, f2, f3 = count()
print f1()
print f2()
print f3()

# 在上面的例子中，每次循环，都创建了一个新的函数，然后，把创建的3个函数都返回了。
# 你可能认为调用f1()，f2()和f3()结果应该是1，4，9，但实际结果是：
# 全部都是9！原因就在于返回的函数引用了变量i，但它并非立刻执行。等到3个函数都返回时，它们所引用的变量i已经变成了3，因此最终结果为9。
# 返回闭包时牢记的一点就是：返回函数不要引用任何循环变量，或者后续会发生变化的变量。

def count_new():
    fs = []
    for i in range(1, 4):
        def f(j):
            def g():
                return j*j
            return g
        fs.append(f(i))
    return fs

f4, f5, f6 = count_new()
print f4()
print f5()
print f6()


def count_new1():
    for i in range(1, 4):
        def f():
            return i * i
        yield f
for f in count():
    print f() 


# 匿名函数
print map(lambda x: x * x, [1, 2, 3, 4, 5, 6, 7, 8, 9])
# 通过对比可以看出，匿名函数lambda x: x * x实际上就是：
def f1(x):
    return x * x
# 关键字lambda表示匿名函数，冒号前面的x表示函数参数。
# 这里的d.items()实际上是将d转换为可迭代对象，迭代对象的元素为（‘lilee’,25）、（‘wangyan’,21）、（‘liqun’,32）、（‘lidaming’,19），items()方法将字典的元素转化为了元组，而这里key参数对应的lambda表达式的意思则是选取元组中的第二个元素作为比较参数（如果写作key=lambda item:item[0]的话则是选取第一个元素作为比较对象，也就是key值作为比较对象。lambda x:y中x表示输出参数，y表示lambda函数的返回值），所以采用这种方法可以对字典的value进行排序。注意排序后的返回值是一个list，而原字典中的名值对被转换为了list中的元组。
# 用匿名函数有个好处，因为函数没有名字，不必担心函数名冲突。此外，匿名函数也是一个函数对象，也可以把匿名函数赋值给一个变量，再利用变量来调用该函数：
f2 = lambda x: x * x
print f2(5)

# 同样，也可以把匿名函数作为返回值返回，比如：
def build(x, y):
    return lambda: x * x + y * y




