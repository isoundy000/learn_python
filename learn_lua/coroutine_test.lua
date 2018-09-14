#!/usr/local/bin/lua
--以下实例演示了以上各个方法的用法：
--coroutine_test.lua文件
co = coroutine.create(
    function(i)
        print("++++++++++")
        print(i);
    end
)

print(coroutine.status(co)) --suspend延缓
print('==================')
coroutine.resume(co, 1) -- 1
print(coroutine.status(co)) --dead
print("----------------")


co = coroutine.wrap(
    function(i)
        print(i);
    end
)

co(1)
print('----------------')

co2 = coroutine.create(
    function()
        for i=1,10 do
            print(i)
            if i == 3 then
                print(coroutine.status(co2))    --running
                print('+++++++++++++')
                print(coroutine.running())      --thread:xxx
                print('+++++++++++++')
            end
            coroutine.yield()
        end
    end
)

coroutine.resume(co2)
coroutine.resume(co2)
coroutine.resume(co2)

print(coroutine.status(co2))
print(coroutine.running())
print('-----------------')


--接下来我们分析一个更详细的实例：
function foo (a)
    print("foo 函数输出", a)
    return coroutine.yield(2 * a) -- 返回  2*a 的值
end

co = coroutine.create(function (a , b)
    print("第一次协同程序执行输出", a, b) -- co-body 1 10
    local r = foo(a + 1)

    print("第二次协同程序执行输出", r)
    local r, s = coroutine.yield(a + b, a - b)  -- a，b的值为第一次调用协同程序时传入

    print("第三次协同程序执行输出", r, s)
    return b, "结束协同程序"                   -- b的值为第二次调用协同程序时传入
end)

print("main", coroutine.resume(co, 1, 10)) -- true, 4
print("--分割线----")
print("main", coroutine.resume(co, "r")) -- true 11 -9
print("---分割线---")
print("main", coroutine.resume(co, "x", "y")) -- true 10 end
print("---分割线---")
print("main", coroutine.resume(co, "x", "y")) -- cannot resume dead coroutine
print("---分割线---")

--以上实例接下如下：
--调用resume，将协同程序唤醒,resume操作成功返回true，否则返回false；
--协同程序运行；
--运行到yield语句；
--yield挂起协同程序，第一次resume返回；（注意：此处yield返回，参数是resume的参数）
--第二次resume，再次唤醒协同程序；（注意：此处resume的参数中，除了第一个参数，剩下的参数将作为yield的参数）
--yield返回；
--协同程序继续运行；
--如果使用的协同程序继续运行完成后继续调用 resume方法则输出：cannot resume dead coroutine
--resume和yield的配合强大之处在于，resume处于主程中，它将外部状态（数据）传入到协同程序内部；而yield则将内部的状态（数据）返回到主程中。

--生产者-消费者问题
--现在我就使用Lua的协同程序来完成生产者-消费者这一经典问题。
local newProductor

function productor()
    local i = 0
    while true do
        i = i + 1
        send(i)     --将生产的物品发送给消费者
    end
end

function consumer()
    while true do
        local i = receive()     -- 从生产者那里得到物品
        print(i)
    end
end

function receive()
    local status, value = coroutine.resume(newProductor)
    return value
end

function send(i)
    coroutine.yield(i)          --x表示需要发送的值，值返回以后，就挂起该协同程序
end

--启动程序
newProductor = coroutine.create(productor)
consumer()



--这一章的例子较难理解，如果把yield()和resume()两个函数的行为描述清楚了，就好理解多了。
--例子再简化一下：
co = coroutine.create(function (a)
    local r = coroutine.yield(a+1)       -- yield()返回a+1给调用它的resume()函数，即2
    print("r=" ..r)                       -- r的值是第2次resume()传进来的，100
end)
status, r = coroutine.resume(co, 1)     -- resume()返回两个值，一个是自身的状态true，一个是yield的返回值2
coroutine.resume(co, 100)     --resume()返回true


--coroutine.creat方法和coroutine.wrap需要特别注意的是这个返回值的类型，功能上有些类似，但并不完全一样。
--coroutine.creat返回的是一个协同程序，类型为thread,需要使用coroutine.resume进行调用；而coroutine.wrap返回的是一个普通的方法(函数)，类型为function，和普通function有同样的使用方法，并且不能使用coroutine.resume进行调用。
--以下代码进行测试：
co_creat = coroutine.create(
    function()
        print("co_creat类型是"..type(co_creat))
    end
)

co_wrap = coroutine.wrap(
    function()
        print("co_wrap类型是"..type(co_wrap))
    end
)

coroutine.resume(co_creat)
co_wrap()
--输出：
--co_creat类型是thread
--co_wrap类型是function

--coroutine.resume方法需要特别注意的一点是，这个方法只要调用就会返回一个boolean值。
--coroutine.resume方法如果调用成功，那么返回true，如果有yield方法，同时返回yield括号里的参数;如果失败，那么返回false，并且带上一句"cannot resume dead coroutine"
--以下代码进行测试：
co_yieldtest = coroutine.create(
    function()
        coroutine.yield()
        coroutine.yield(1)
        return 2
    end
)

for i = 1,4 do
    print("第"..i.."次调用协程:", coroutine.resume(co_yieldtest))
end
--输出：
--第1次调用协程:    true
--第2次调用协程:    true    1
--第3次调用协程:    true    2
--第4次调用协程:    false    cannot resume dead coroutine


--coroutine.creat方法只要建立了一个协程 ，那么这个协程的状态默认就是suspend。使用resume方法启动后，会变成running状态；遇到yield时将状态设为suspend；如果遇到return，那么将协程的状态改为dead。
--coroutine.resume方法需要特别注意的一点是，这个方法只要调用就会返回一个boolean值。
--coroutine.resume方法如果调用成功，那么返回true；如果有yield方法，同时返回yield括号里的参数；如果没有yield，那么继续运行直到协程结束；直到遇到return，将协程的状态改为dead，并同时返回return的值。
--coroutine.resume方法如果调用失败(调用状态为dead的协程会导致失败)，那么返回false，并且带上一句"cannot resume dead coroutine"
--以下代码进行测试：
function yieldReturn(arg) return arg end

co_yieldtest = coroutine.create(
    function()
        print("启动协程状态"..coroutine.status(co_yieldtest))
        print("--")
        coroutine.yield()
        coroutine.yield(1)
        coroutine.yield(print("第3次调用"))
        coroutine.yield(yieldReturn("第4次调用"))
        return 2
    end
)

    print("启动前协程状态"..coroutine.status(co_yieldtest))
    print("--")

for i = 1,6 do
    print("第"..i.."次调用协程:", coroutine.resume(co_yieldtest))
    print("当前协程状态"..coroutine.status(co_yieldtest))
    print("--")
end
--输出：
--启动前协程状态suspended
--
--启动协程状态running
--
--第1次调用协程:    true
--当前协程状态suspended
--
--第2次调用协程:    true    1
--当前协程状态suspended
--
--第3次调用
--第3次调用协程:    true
--当前协程状态suspended
--
--第4次调用协程:    true    第4次调用
--当前协程状态suspended
--
--第5次调用协程:    true    2
--当前协程状态dead
--
--第6次调用协程:    false    cannot resume dead coroutine
--当前协程状态dead
--


--挂起协程： yield 除了挂起协程外，还可以同时返回数据给 resume ,并且还可以同时定义下一次唤醒时需要传递的参数。
print();
cor = coroutine.create(function(a)
    print("参数 a值为：", a);
    local b, c = coroutine.yield(a + 1); --这里表示挂起协程，并且将a+1的值进行返回，并且指定下一次唤醒需要 b,c 两个参数。
    print("参数 b,c值分别为：", b, c);
    return b * c; --协程结束，并且返回 b*c 的值。
end);

print("第一次调用：", coroutine.resume(cor, 1));
print("第二次调用：", coroutine.resume(cor, 2, 2));
print("第三次调用：", coroutine.resume(cor));
--执行结果（结果中 true 表示本次调用成功）：
--参数 a值为：    1
--第一次调用：    true    2
--参数 b,c值分别为：    2    2
--第二次调用：    true    4
--第三次调用：    false    cannot resume dead coroutine