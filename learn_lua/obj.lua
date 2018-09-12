#!/usr/local/bin/lua

Account = {balance = 0}

function Account.withdraw(v)
    Account.balance = Account.balance - v
end

print(Account.withdraw(100.00))

-- 一个简单实例
-- Meta class
Rectangle = {area = 0, length = 0, breadth = 0}

-- 派生类的方法 new
function Rectangle:new(o, length, breadth)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    self.length = length or 0
    self.breadth = breadth or 0
    self.area = length * breadth
    return o
end

-- 派生类的方法 printArea
function Rectangle:printArea( ... )
    print("矩形面积为", self.area)
end

--创建对象
r = Rectangle:new(nil, 10, 20)
--访问属性
print(r.length)
--访问成员函数
print(r:printArea())
print('------------------------------------')

--完整实例
-- Meta class
Shape = {area = 0}

-- 基础类方法 new
function Shape:new( o, side )
    print('4444444444', o, side)
    o = o or {}
    print('33333333333', o, side)
    setmetatable(o, self)
    self.__index = self
    side = side or 0
    self.area = side * side
    return o
end

-- 基础类方法 printArea
function Shape:printArea( ... )
    print("面积为", self.area)
end

-- 创建对象
myshape = Shape:new(nil, 10)
myshape:printArea()

-- Lua 继承
-- Derived class method new. 派生类方法 new
Square = Shape:new()
function Square:new( o, side )
    o = o or Shape:new(o, side)
    setmetatable(o, self)
    self.__index = self
    return o
end

-- 完整实例
-- 以下实例我们继承了一个简单的类，来扩展派生类的方法，派生类中保留了继承类的成员变量和方法：
-- 派生类方法 printArea
function Square:printArea( ... )
    print("正方形面积为", self.area)
end

-- 创建对象
-- 接下来的实例，Square 对象继承了 Shape 类:
mysquare = Square:new(nil, 10)
mysquare:printArea()

Rectangle = Square:new()
-- 派生类方法 new
function Rectangle:new( o, length, breadth)
    print('11111111111', o)
    o = o or Shape:new(o)
    print('22222222222', Shape:new(o))
    setmetatable(o, self)
    self.__index = self
    self.area = length * breadth
    return o
end

-- 派生类方法 printArea
function Rectangle:printArea( ... )
    print("矩形面积为", self.area)
end

-- 创建对象
myrectangle = Rectangle:new(nil, 10, 20)
myrectangle:printArea()

-- 函数重写
-- Lua 中我们可以重写基础类的函数，在派生类中定义自己的实现方式：
function Square:printArea( ... )
    print("正方形面积 ", self.area)
end

print('====================================')
-- 按实例的写法，每次new新实例的时候都需要将第一个变量的值设为nil,很不方便。可以稍做变形，把变量o放在函数里创建，免去麻烦。
--创建一个类，表示四边形
local RectAngle = {length, width, area}     --声明类名和类成员变量

function RectAngle:new( len, wid)    --声明新建实例的New方法
    local o = {
        --设定各个项的值
        length = len or 0,
        width = wid or 0,
        area = len * wid
    }
    setmetatable(o, {__index = self})  --将自身的表映射到新new出来的表中
    return o
end

function RectAngle:getInfo()            --获取表内信息的方法
    return self.length, self.width, self.area
end

a = RectAngle:new(10, 20)
print(a:getInfo())

b = RectAngle:new(10, 10)
print(b:getInfo())
print(a:getInfo())
print(string.rep('*', 30))
-- 补充： . 与 : 的区别在于使用 : 定义的函数隐含 self 参数，使用 : 调用函数会自动传入 table 至 self 参数，示例：
classA = {}

function classA:getob( name )
    print(self)
    ob = {}
    setmetatable(ob, self)
    self.__index = self
    self.name = name
    return ob
end

function classA:getself( ... )
    return self
end


c1 = classA:getob("A")
c2 = classA:getob("B")
print(string.rep("*", 30))
print(c1:getself())
print(c2:getself())
print(string.rep("*", 30))
----------------------继承------------------------
classB = classA:getob()     ----非常重要，用于获取继承的self
function classB:getob( name, address )
    ob = classA:getob(name)
    setmetatable(ob, self)
    self.__index = self
    self.address = address
    return ob
end

c3 = classB:getob("gray.yang", "shenzhen")
print(c3:getself())
print(string.rep("*", 50))

-- 模拟类和继承
classA = {}

function classA.new(cls, ... )      --定义类方法时使用"."号，不适用隐式传参
    this = {}
    setmetatable(this, cls)
    cls.__index = cls         --将元表的__index设为自身，访问表的属性不存在时会搜索元表
    cls.init(this, ...)       --初始化表，注意访问类的方法都是"."，此时不会隐式传入参数
    return this
end

function classA.init( self, name )
    self.name = name
end

function classA.getname( self )
    return self.name
end

p = classA:new("gray.yang")
print(p:getname())
print(string.rep("*", 50))

-- 模拟继承
classB = classA:new()                       --获得实例

function classB.new( cls, ... )
    this = {}
    setmetatable(this, cls)
    cls.__index = cls
    cls.init(this,...)
    return this
end

function classB.init( self, name, address )
    super = getmetatable(self)
    super:init(name)                        --使用父类初始化
    self.address = address
end


function classB.getaddress( self )
    return self.address
end

b = classB:new("tom.li", "shenzhen")
print("getbname==============>", b:getname())
print("getbaddress===========>", b:getaddress())

-- 多重继承
-- 在table 'plist'中查找'k'
local function search( k, plist )
    for i=1, #plist do
        local v = plist[i][k]      -- 尝试第i个基类
        if v then return v end
    end
end

function createClass( ... )
    local c = {}                   -- 新类
    local parents = { ... }

    -- 类在其父类列表中的搜索方法
    setmetatable(c, {__index = function( t, k )
        return search(k, parents)
    end})

    -- 将'c'作为其实例的元表
    c.__index = c

    -- 为这个新类定义一个新的构造函数
    function c:new( o )
        o = o or {}
        setmetatable(o, c)
        return o
    end
    return c                     -- 返回新类
end

-- 类Named
Named = {}
function Named:getname()
    return self.name
end

function Named:setname( n )
    self.name = n
end

--类Account
Account = {balance = 0}
function Account:withdraw( w )
    self.balance = self.balance - v
end

-- 创建一个新类NamedAccount，同时从Account和Named派生
NamedAccount = createClass(Account, Named)
account = NamedAccount:new()
account:setname("Ives")
print(account:getname())                -- 输出 Ives
print(string.rep("*", 50))

-- 一个简单的面向对象实现
--[[
Lua 中使用":"实现面向对象方式的调用。":"只是语法糖，它同时在方法的声明与实现中增加了一个
名为 self 的隐藏参数，这个参数就是对象本身。
]]

--实例：
Account = {balance = 0};

--生成对象
function Account:new(o)
    o = o or {};                    --如果用户没有提供对象，则创建一个。
    setmetatable(o, self);          --将 Account 作为新创建的对象元表
    self.__index = self;            --将新对象元表的 __index 指向为 Account（这样新对象就可以通过索引来访问 Account 的值了）
    return o;                       --将新对象返回
end

--存款
function Account:deposit(v)
    self.balance = self.balance + v;
end

--取款
function Account:withdraw(v)
    self.balance = self.balance - v;
end

--查询
function Account:demand()
    print(self.balance);
end

--创建对象
myAccount = Account:new();
--通过索引访问
print(myAccount.balance);
--调用函数
myAccount:deposit(100);
myAccount:withdraw(50);
myAccount:demand();