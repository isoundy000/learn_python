# -*- encoding: utf-8 -*-
'''
Created on 2017年11月8日

@author: houguangdong
'''

# Python itertools模块详解
# itertools用于高效循环的迭代函数集合
# 组成
# 总体，整体了解
# 无限迭代器
# 迭代器         参数         结果                                                例子
# count()     start, [step]   start, start+step, start+2*step, ...                count(10) --> 10 11 12 13 14 ...
# cycle()     p               p0, p1, ... plast, p0, p1, ...                      cycle('ABCD') --> A B C D A B C D ...
# repeat()    elem [,n]       elem, elem, elem, ... endlessly or up to n times    repeat(10, 3) --> 10 10 10

# 处理输入序列迭代器
# 迭代器          参数            结果                                        例子
# chain()     p, q, ...           p0, p1, ... plast, q0, q1, ...              chain('ABC', 'DEF') --> A B C D E F
# compress()  data, selectors     (d[0] if s[0]), (d[1] if s[1]), ...         compress('ABCDEF', [1,0,1,0,1,1]) --> A C E F
# dropwhile() pred, seq           seq[n], seq[n+1], starting when pred fails  dropwhile(lambda x: x<5, [1,4,6,4,1]) --> 6 4 1
# groupby()   iterable[, keyfunc] sub-iterators grouped by value of keyfunc(v)
# ifilter()   pred, seq           elements of seq where pred(elem) is True    ifilter(lambda x: x%2, range(10)) --> 1 3 5 7 9
# ifilterfalse()  pred, seq       elements of seq where pred(elem) is False   ifilterfalse(lambda x: x%2, range(10)) --> 0 2 4 6 8
# islice()    seq, [start,] stop [, step] elements from seq[start:stop:step]  islice('ABCDEFG', 2, None) --> C D E F G
# imap()      func, p, q, ...     func(p0, q0), func(p1, q1), ...             imap(pow, (2,3,10), (5,2,3)) --> 32 9 1000
# starmap()   func, seq           func(*seq[0]), func(*seq[1]), ...           starmap(pow, [(2,5), (3,2), (10,3)]) --> 32 9 1000
# tee()       it, n               it1, it2 , ... itn splits one iterator into n
# takewhile() pred, seq           seq[0], seq[1], until pred fails            takewhile(lambda x: x<5, [1,4,6,4,1]) --> 1 4
# izip()      p, q, ...           (p[0], q[0]), (p[1], q[1]), ...             izip('ABCD', 'xy') --> Ax By
# izip_longest()  p, q, ...       (p[0], q[0]), (p[1], q[1]), ...             izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-

# 组合生成器
# 迭代器          参数                        结果
# product()       p, q, ... [repeat=1]        cartesian product, equivalent to a nested for-loop
# permutations()  p[, r]                      r-length tuples, all possible orderings, no repeated elements
# combinations()  p, r                        r-length tuples, in sorted order, no repeated elements
# combinations_with_replacement() p, r        r-length tuples, in sorted order, with repeated elements
# product('ABCD', repeat=2)                   AA AB AC AD BA BB BC BD CA CB CC CD DA DB DC DD
# permutations('ABCD', 2)                     AB AC AD BA BC BD CA CB CD DA DB DC
# combinations('ABCD', 2)                     AB AC AD BC BD CD
# combinations_with_replacement('ABCD', 2)    AA AB AC AD BB BC BD CC CD DD

# 第一部分
# itertools.count(start=0, step=1)
创建一个迭代器，生成从n开始的连续整数，如果忽略n，则从0开始计算（注意：此迭代器不支持长整数）
如果超出了sys.maxint，计数器将溢出并继续从-sys.maxint-1开始计算。
定义
复制代码 代码如下:

def count(start=0, step=1):
    # count(10) --> 10 11 12 13 14 ...
    # count(2.5, 0.5) -> 2.5 3.0 3.5 ...
    n = start
    while True:
        yield n
        n += step

等同于(start + step * i for i in count())
使用
复制代码 代码如下:

from itertools import *
for i in izip(count(1), ['a', 'b', 'c']):
    print i
(1, 'a')
(2, 'b')
(3, 'c')
itertools.repeat(object[, times])
创建一个迭代器，重复生成object，times（如果已提供）指定重复计数，如果未提供times，将无止尽返回该对象。
定义
复制代码 代码如下:

def repeat(object, times=None):
    # repeat(10, 3) --> 10 10 10
    if times is None:
        while True:
            yield object
    else:
        for i in xrange(times):
            yield object

使用
复制代码 代码如下:

from itertools import *
for i in repeat('over-and-over', 5):
    print i
over-and-over
over-and-over
over-and-over
over-and-over
over-and-over
第二部分
itertools.chain(*iterables)
将多个迭代器作为参数, 但只返回单个迭代器, 它产生所有参数迭代器的内容, 就好像他们是来自于一个单一的序列.
复制代码 代码如下:

def chain(*iterables):
    # chain('ABC', 'DEF') --> A B C D E F
    for it in iterables:
        for element in it:
            yield element

使用
复制代码 代码如下:

from itertools import *
for i in chain([1, 2, 3], ['a', 'b', 'c']):
    print i
1
2
3
a
b
c

from itertools import chain, imap
def flatmap(f, items):
    return chain.from_iterable(imap(f, items))
>>> list(flatmap(os.listdir, dirs))
>>> ['settings.py', 'wsgi.py', 'templates', 'app.py',
     'templates', 'index.html, 'config.json']
itertools.compress(data, selectors)
提供一个选择列表，对原始数据进行筛选
复制代码 代码如下:

def compress(data, selectors):
    # compress('ABCDEF', [1,0,1,0,1,1]) --> A C E F
    return (d for d, s in izip(data, selectors) if s)
itertools.dropwhile(predicate, iterable)

创建一个迭代器，只要函数predicate(item)为True，就丢弃iterable中的项，如果predicate返回False，就会生成iterable中的项和所有后续项。
即：在条件为false之后的第一次, 返回迭代器中剩下来的项.
复制代码 代码如下:

def dropwhile(predicate, iterable):
    # dropwhile(lambda x: x<5, [1,4,6,4,1]) --> 6 4 1
    iterable = iter(iterable)
    for x in iterable:
        if not predicate(x):
            yield x
            break
    for x in iterable:
        yield x
使用
复制代码 代码如下:

from itertools import *
def should_drop(x):
    print 'Testing:', x
    return (x<1)
for i in dropwhile(should_drop, [ -1, 0, 1, 2, 3, 4, 1, -2 ]):
    print 'Yielding:', i
Testing: -1
Testing: 0
Testing: 1
Yielding: 1
Yielding: 2
Yielding: 3
Yielding: 4
Yielding: 1
Yielding: -2
itertools.groupby(iterable[, key])
返回一个产生按照key进行分组后的值集合的迭代器.
如果iterable在多次连续迭代中生成了同一项，则会定义一个组，如果将此函数应用一个分类列表，那么分组将定义该列表中的所有唯一项，key（如果已提供）是一个函数，应用于每一项，如果此函数存在返回值，该值将用于后续项而不是该项本身进行比较，此函数返回的迭代器生成元素(key, group)，其中key是分组的键值，group是迭代器，生成组成该组的所有项。
即：按照keyfunc函数对序列每个元素执行后的结果分组(每个分组是一个迭代器), 返回这些分组的迭代器
等价于
复制代码 代码如下:

class groupby(object):
    # [k for k, g in groupby('AAAABBBCCDAABBB')] --> A B C D A B
    # [list(g) for k, g in groupby('AAAABBBCCD')] --> AAAA BBB CC D
    def __init__(self, iterable, key=None):
        if key is None:
            key = lambda x: x
        self.keyfunc = key
        self.it = iter(iterable)
        self.tgtkey = self.currkey = self.currvalue = object()
    def __iter__(self):
        return self
    def next(self):
        while self.currkey == self.tgtkey:
            self.currvalue = next(self.it)    # Exit on StopIteration
            self.currkey = self.keyfunc(self.currvalue)
        self.tgtkey = self.currkey
        return (self.currkey, self._grouper(self.tgtkey))
    def _grouper(self, tgtkey):
        while self.currkey == tgtkey:
            yield self.currvalue
            self.currvalue = next(self.it)    # Exit on StopIteration
            self.currkey = self.keyfunc(self.currvalue)
应用
复制代码 代码如下:

from itertools import groupby
qs = [{'date' : 1},{'date' : 2}]
[(name, list(group)) for name, group in itertools.groupby(qs, lambda p:p['date'])]
Out[77]: [(1, [{'date': 1}]), (2, [{'date': 2}])]

>>> from itertools import *
>>> a = ['aa', 'ab', 'abc', 'bcd', 'abcde']
>>> for i, k in groupby(a, len):
...     print i, list(k)
...
2 ['aa', 'ab']
3 ['abc', 'bcd']
5 ['abcde']
另一个例子
复制代码 代码如下:

from itertools import *
from operator import itemgetter
d = dict(a=1, b=2, c=1, d=2, e=1, f=2, g=3)
di = sorted(d.iteritems(), key=itemgetter(1))
for k, g in groupby(di, key=itemgetter(1)):
    print k, map(itemgetter(0), g)

1 ['a', 'c', 'e']
2 ['b', 'd', 'f']
3 ['g']
itertools.ifilter(predicate, iterable)
返回的是迭代器类似于针对列表的内置函数 filter() , 它只包括当测试函数返回true时的项. 它不同于 dropwhile()
创建一个迭代器，仅生成iterable中predicate(item)为True的项，如果predicate为None，将返回iterable中所有计算为True的项
对函数func执行返回真的元素的迭代器
复制代码 代码如下:

def ifilter(predicate, iterable):
    # ifilter(lambda x: x%2, range(10)) --> 1 3 5 7 9
    if predicate is None:
        predicate = bool
    for x in iterable:
        if predicate(x):
            yield x
使用
复制代码 代码如下:

from itertools import *
def check_item(x):
    print 'Testing:', x
    return (x<1)
for i in ifilter(check_item, [ -1, 0, 1, 2, 3, 4, 1, -2 ]):
    print 'Yielding:', i
Testing: -1
Yielding: -1
Testing: 0
Yielding: 0
Testing: 1
Testing: 2
Testing: 3
Testing: 4
Testing: 1
Testing: -2
Yielding: -2
itertools.ifilterfalse(predicate, iterable)
和ifilter(函数相反 ， 返回一个包含那些测试函数返回false的项的迭代器)
创建一个迭代器，仅生成iterable中predicate(item)为False的项，如果predicate为None，则返回iterable中所有计算为False的项 对函数func执行返回假的元素的迭代器
复制代码 代码如下:

def ifilterfalse(predicate, iterable):
    # ifilterfalse(lambda x: x%2, range(10)) --> 0 2 4 6 8
    if predicate is None:
        predicate = bool
    for x in iterable:
        if not predicate(x):
            yield x
使用
复制代码 代码如下:

from itertools import *
def check_item(x):
    print 'Testing:', x
    return (x<1)
for i in ifilterfalse(check_item, [ -1, 0, 1, 2, 3, 4, 1, -2 ]):
    print 'Yielding:', i
Testing: -1
Testing: 0
Testing: 1
Yielding: 1
Testing: 2
Yielding: 2
Testing: 3
Yielding: 3
Testing: 4
Yielding: 4
Testing: 1
Yielding: 1
Testing: -2
itertools.islice(iterable, stop)
itertools.islice(iterable, start, stop[, step])
返回的迭代器是返回了输入迭代器根据索引来选取的项
创建一个迭代器，生成项的方式类似于切片返回值： iterable[start : stop : step]，将跳过前start个项，迭代在stop所指定的位置停止，step指定用于跳过项的步幅。 与切片不同，负值不会用于任何start，stop和step， 如果省略了start，迭代将从0开始，如果省略了step，步幅将采用1.
返回序列seq的从start开始到stop结束的步长为step的元素的迭代器
复制代码 代码如下:

def islice(iterable, *args):
    # islice('ABCDEFG', 2) --> A B
    # islice('ABCDEFG', 2, 4) --> C D
    # islice('ABCDEFG', 2, None) --> C D E F G
    # islice('ABCDEFG', 0, None, 2) --> A C E G
    s = slice(*args)
    it = iter(xrange(s.start or 0, s.stop or sys.maxint, s.step or 1))
    nexti = next(it)
    for i, element in enumerate(iterable):
        if i == nexti:
            yield element
            nexti = next(it)
使用
复制代码 代码如下:

from itertools import *
print 'Stop at 5:'
for i in islice(count(), 5):
    print i
print 'Start at 5, Stop at 10:'
for i in islice(count(), 5, 10):
    print i
print 'By tens to 100:'
for i in islice(count(), 0, 100, 10):
    print i
Stop at 5:
0
1
2
3
4
Start at 5, Stop at 10:
5
6
7
8
9
By tens to 100:
0
10
20
30
40
50
60
70
80
90
itertools.imap(function, *iterables)
创建一个迭代器，生成项function(i1, i2, ..., iN)，其中i1，i2...iN分别来自迭代器iter1，iter2 ... iterN，如果function为None，则返回(i1, i2, ..., iN)形式的元组，只要提供的一个迭代器不再生成值，迭代就会停止。
即：返回一个迭代器, 它是调用了一个其值在输入迭代器上的函数, 返回结果. 它类似于内置函数 map() , 只是前者在任意输入迭代器结束后就停止(而不是插入None值来补全所有的输入).
返回序列每个元素被func执行后返回值的序列的迭代器
复制代码 代码如下:

def imap(function, *iterables):
    # imap(pow, (2,3,10), (5,2,3)) --> 32 9 1000
    iterables = map(iter, iterables)
    while True:
        args = [next(it) for it in iterables]
        if function is None:
            yield tuple(args)
        else:
            yield function(*args)
使用
复制代码 代码如下:

from itertools import *
print 'Doubles:'
for i in imap(lambda x:2*x, xrange(5)):
    print i
print 'Multiples:'
for i in imap(lambda x,y:(x, y, x*y), xrange(5), xrange(5,10)):
    print '%d * %d = %d' % i
Doubles:
0
2
4
6
8
Multiples:
0 * 5 = 0
1 * 6 = 6
2 * 7 = 14
3 * 8 = 24
4 * 9 = 36
itertools.starmap(function, iterable)
创建一个迭代器，生成值func(*item),其中item来自iterable，只有当iterable生成的项适用于这种调用函数的方式时，此函数才有效。
对序列seq的每个元素作为func的参数列表执行, 返回执行结果的迭代器
复制代码 代码如下:

def starmap(function, iterable):
    # starmap(pow, [(2,5), (3,2), (10,3)]) --> 32 9 1000
    for args in iterable:
        yield function(*args)

使用
复制代码 代码如下:

from itertools import *
values = [(0, 5), (1, 6), (2, 7), (3, 8), (4, 9)]
for i in starmap(lambda x,y:(x, y, x*y), values):
    print '%d * %d = %d' % i
0 * 5 = 0
1 * 6 = 6
2 * 7 = 14
3 * 8 = 24
4 * 9 = 36
itertools.tee(iterable[, n=2])
返回一些基于单个原始输入的独立迭代器(默认为2). 它和Unix上的tee工具有点语义相似, 也就是说它们都重复读取输入设备中的值并将值写入到一个命名文件和标准输出中
从iterable创建n个独立的迭代器，创建的迭代器以n元组的形式返回，n的默认值为2，此函数适用于任何可迭代的对象，但是，为了克隆原始迭代器，生成的项会被缓存，并在所有新创建的迭代器中使用，一定要注意，不要在调用tee()之后使用原始迭代器iterable，否则缓存机制可能无法正确工作。
把一个迭代器分为n个迭代器, 返回一个元组.默认是两个
复制代码 代码如下:

def tee(iterable, n=2):
    it = iter(iterable)
    deques = [collections.deque() for i in range(n)]
    def gen(mydeque):
        while True:
            if not mydeque:             # when the local deque is empty
                newval = next(it)       # fetch a new value and
                for d in deques:        # load it to all the deques
                    d.append(newval)
            yield mydeque.popleft()
    return tuple(gen(d) for d in deques)
使用
复制代码 代码如下:

from itertools import *
r = islice(count(), 5)
i1, i2 = tee(r)
for i in i1:
    print 'i1:', i
for i in i2:
    print 'i2:', i
i1: 0
i1: 1
i1: 2
i1: 3
i1: 4
i2: 0
i2: 1
i2: 2
i2: 3
i2: 4
itertools.takewhile(predicate, iterable)
和dropwhile相反
创建一个迭代器，生成iterable中predicate(item)为True的项，只要predicate计算为False，迭代就会立即停止。
即：从序列的头开始, 直到执行函数func失败.
复制代码 代码如下:

def takewhile(predicate, iterable):
    # takewhile(lambda x: x<5, [1,4,6,4,1]) --> 1 4
    for x in iterable:
        if predicate(x):
            yield x
        else:
            break
使用
复制代码 代码如下:

from itertools import *
def should_take(x):
    print 'Testing:', x
    return (x<2)
for i in takewhile(should_take, [ -1, 0, 1, 2, 3, 4, 1, -2 ]):
    print 'Yielding:', i
Testing: -1
Yielding: -1
Testing: 0
Yielding: 0
Testing: 1
Yielding: 1
Testing: 2
itertools.izip(*iterables)
返回一个合并了多个迭代器为一个元组的迭代器. 它类似于内置函数zip(), 只是它返回的是一个迭代器而不是一个列表
创建一个迭代器，生成元组(i1, i2, ... iN)，其中i1，i2 ... iN 分别来自迭代器iter1，iter2 ... iterN，只要提供的某个迭代器不再生成值，迭代就会停止，此函数生成的值与内置的zip()函数相同。
复制代码 代码如下:

izip(iter1, iter2, ... iterN):
返回:(it1[0],it2 [0], it3[0], ..), (it1[1], it2[1], it3[1], ..)...
def izip(*iterables):
    # izip('ABCD', 'xy') --> Ax By
    iterators = map(iter, iterables)
    while iterators:
        yield tuple(map(next, iterators))
使用
复制代码 代码如下:

from itertools import *
for i in izip([1, 2, 3], ['a', 'b', 'c']):
    print i
(1, 'a')
(2, 'b')
(3, 'c')

itertools.izip_longest(*iterables[, fillvalue])
与izip()相同，但是迭代过程会持续到所有输入迭代变量iter1,iter2等都耗尽为止，如果没有使用fillvalue关键字参数指定不同的值，则使用None来填充已经使用的迭代变量的值。
复制代码 代码如下:

class ZipExhausted(Exception):
    pass
def izip_longest(*args, **kwds):
    # izip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
    fillvalue = kwds.get('fillvalue')
    counter = [len(args) - 1]
    def sentinel():
        if not counter[0]:
            raise ZipExhausted
        counter[0] -= 1
        yield fillvalue
    fillers = repeat(fillvalue)
    iterators = [chain(it, sentinel(), fillers) for it in args]
    try:
        while iterators:
            yield tuple(map(next, iterators))
    except ZipExhausted:
        pass
第三部分
itertools.product(*iterables[, repeat])
笛卡尔积
创建一个迭代器，生成表示item1，item2等中的项目的笛卡尔积的元组，repeat是一个关键字参数，指定重复生成序列的次数。
复制代码 代码如下:

def product(*args, **kwds):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)
例子
复制代码 代码如下:

import itertools
a = (1, 2, 3)
b = ('A', 'B', 'C')
c = itertools.product(a,b)
for elem in c:
    print elem
(1, 'A')
(1, 'B')
(1, 'C')
(2, 'A')
(2, 'B')
(2, 'C')
(3, 'A')
(3, 'B')
(3, 'C')
itertools.permutations(iterable[, r])
排列
创建一个迭代器，返回iterable中所有长度为r的项目序列，如果省略了r，那么序列的长度与iterable中的项目数量相同： 返回p中任意取r个元素做排列的元组的迭代器
复制代码 代码如下:

def permutations(iterable, r=None):
    # permutations('ABCD', 2) --> AB AC AD BA BC BD CA CB CD DA DB DC
    # permutations(range(3)) --> 012 021 102 120 201 210
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    if r > n:
        return
    indices = range(n)
    cycles = range(n, n-r, -1)
    yield tuple(pool[i] for i in indices[:r])
    while n:
        for i in reversed(range(r)):
            cycles[i] -= 1
            if cycles[i] == 0:
                indices[i:] = indices[i+1:] + indices[i:i+1]
                cycles[i] = n - i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield tuple(pool[i] for i in indices[:r])
                break
        else:
            return
也可以用product实现
def permutations(iterable, r=None):
    pool = tuple(iterable)
    n = len(pool)
    r = n if r is None else r
    for indices in product(range(n), repeat=r):
        if len(set(indices)) == r:
            yield tuple(pool[i] for i in indices)
itertools.combinations(iterable, r)
创建一个迭代器，返回iterable中所有长度为r的子序列，返回的子序列中的项按输入iterable中的顺序排序 (不带重复)
复制代码 代码如下:

def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = range(r)
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)
#或者
def combinations(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    for indices in permutations(range(n), r):
        if sorted(indices) == list(indices):
            yield tuple(pool[i] for i in indices)
itertools.combinations_with_replacement(iterable, r)
创建一个迭代器，返回iterable中所有长度为r的子序列，返回的子序列中的项按输入iterable中的顺序排序 (带重复)
复制代码 代码如下:

def combinations_with_replacement(iterable, r):
    # combinations_with_replacement('ABC', 2) --> AA AB AC BB BC CC
    pool = tuple(iterable)
    n = len(pool)
    if not n and r:
        return
    indices = [0] * r
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != n - 1:
                break
        else:
            return
        indices[i:] = [indices[i] + 1] * (r - i)
        yield tuple(pool[i] for i in indices)
或者
def combinations_with_replacement(iterable, r):
    pool = tuple(iterable)
    n = len(pool)
    for indices in product(range(n), repeat=r):
        if sorted(indices) == list(indices):
            yield tuple(pool[i] for i in indices)
第四部分
扩展
使用现有扩展功能
复制代码 代码如下:

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))
def tabulate(function, start=0):
    "Return function(0), function(1), ..."
    return imap(function, count(start))
def consume(iterator, n):
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)
def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(islice(iterable, n, None), default)
def quantify(iterable, pred=bool):
    "Count how many times the predicate is true"
    return sum(imap(pred, iterable))
def padnone(iterable):
    """Returns the sequence elements and then returns None indefinitely.
    Useful for emulating the behavior of the built-in map() function.
    """
    return chain(iterable, repeat(None))
def ncycles(iterable, n):
    "Returns the sequence elements n times"
    return chain.from_iterable(repeat(tuple(iterable), n))
def dotproduct(vec1, vec2):
    return sum(imap(operator.mul, vec1, vec2))
def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)
def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.
    Example:  repeatfunc(random.random)
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)
def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))
def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element
def unique_justseen(iterable, key=None):
    "List unique elements, preserving order. Remember only the element just seen."
    # unique_justseen('AAAABBBCCDAABBB') --> A B C D A B
    # unique_justseen('ABBCcAD', str.lower) --> A B C A D
    return imap(next, imap(itemgetter(1), groupby(iterable, key)))
def iter_except(func, exception, first=None):
    """ Call a function repeatedly until an exception is raised.
    Converts a call-until-exception interface to an iterator interface.
    Like __builtin__.iter(func, sentinel) but uses an exception instead
    of a sentinel to end the loop.
    Examples:
        bsddbiter = iter_except(db.next, bsddb.error, db.first)
        heapiter = iter_except(functools.partial(heappop, h), IndexError)
        dictiter = iter_except(d.popitem, KeyError)
        dequeiter = iter_except(d.popleft, IndexError)
        queueiter = iter_except(q.get_nowait, Queue.Empty)
        setiter = iter_except(s.pop, KeyError)
    """
    try:
        if first is not None:
            yield first()
        while 1:
            yield func()
    except exception:
        pass
def random_product(*args, **kwds):
    "Random selection from itertools.product(*args, **kwds)"
    pools = map(tuple, args) * kwds.get('repeat', 1)
    return tuple(random.choice(pool) for pool in pools)
def random_permutation(iterable, r=None):
    "Random selection from itertools.permutations(iterable, r)"
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(random.sample(pool, r))
def random_combination(iterable, r):
    "Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(xrange(n), r))
    return tuple(pool[i] for i in indices)
def random_combination_with_replacement(iterable, r):
    "Random selection from itertools.combinations_with_replacement(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.randrange(n) for i in xrange(r))
    return tuple(pool[i] for i in indices)
def tee_lookahead(t, i):
    """Inspect the i-th upcomping value from a tee object
    while leaving the tee object at its current position.
    Raise an IndexError if the underlying iterator doesn't
    have enough values.
    """
    for value in islice(t.__copy__(), i, None):
        return value
    raise IndexError(i)
自定义扩展
将序列按大小切分,更好的性能
复制代码 代码如下:

from itertools import chain, islice
def chunks(iterable, size, format=iter):
    it = iter(iterable)
    while True:
        yield format(chain((it.next(),), islice(it, size - 1)))
>>> l = ["a", "b", "c", "d", "e", "f", "g"]
>>> for chunk in chunks(l, 3, tuple):...
        print chunk...
("a", "b", "c")
("d", "e", "f")
("g",)
补充
迭代工具，你最好的朋友
迭代工具模块包含了操做指定的函数用于操作迭代器。想复制一个迭代器出来？链接两个迭代器？以one liner（这里的one-liner只需一行代码能搞定的任务)用内嵌的列表组合一组值？不使用list创建Map/Zip？···，你要做的就是 import itertools，举个例子吧：
四匹马赛跑到达终点排名的所有可能性：
复制代码 代码如下:

>>> horses = [1, 2, 3, 4]
>>> races = itertools.permutations(horses)
>>> print(races)
<itertools.permutations object at 0xb754f1dc]]>
>>> print(list(itertools.permutations(horses)))
[(1, 2, 3, 4),
 (1, 2, 4, 3),
 (1, 3, 2, 4),
 (1, 3, 4, 2),
 (1, 4, 2, 3),
 (1, 4, 3, 2),
 (2, 1, 3, 4),
 (2, 1, 4, 3),
 (2, 3, 1, 4),
 (2, 3, 4, 1),
 (2, 4, 1, 3),
 (2, 4, 3, 1),
 (3, 1, 2, 4),
 (3, 1, 4, 2),
 (3, 2, 1, 4),
 (3, 2, 4, 1),
 (3, 4, 1, 2),
 (3, 4, 2, 1),
 (4, 1, 2, 3),
 (4, 1, 3, 2),
 (4, 2, 1, 3),
 (4, 2, 3, 1),
 (4, 3, 1, 2),
 (4, 3, 2, 1)]
理解迭代的内部机制： 迭代(iteration）就是对可迭代对象（iterables，实现了__iter__()方法）和迭代器（iterators，实现了__next__()方法）的一个操作过程。可迭代对象是任何可返回一个迭代器的对象，迭代器是应用在迭代对象中迭代的对象，换一种方式说的话就是：iterable对象的__iter__()方法可以返回iterator对象，iterator通过调用next()方法获取其中的每一个值(译者注)，读者可以结合Java API中的 Iterable接口和Iterator接口进行类比。
