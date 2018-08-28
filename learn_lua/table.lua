#!/usr/local/bin/lua

--简单的table
mytable = {}
print("mytable 的类型是", type(mytable))
mytable[1] = "Lua"
mytable["wow"] = "修改前"
print("mytable 索引为1的元算是", mytable[1])
print("mytable 索引为wow的元素是", mytable["wow"])


--alternatetable和mytable的是指同一个table
alternatetable = mytable

print("alternatetable 索引为 1 的元素是 ", alternatetable[1])
print("alternatetable 索引为 wow 的元素是 ", alternatetable["wow"])

alternatetable["wow"] = "修改后"

print("mytable索引为wow的元素是", mytable["wow"])

--释放变量
alternatetable = nil
print("alternatetable是", alternatetable)


--mytable仍然可以访问
print("mytable 索引为wow的元素是", mytable["wow"])

mytable = nil;
print("mytable 是", mytable)


--Table 连接
--我们可以使用 concat() 方法来连接两个 table:
fruits = {"banana", "orange", "apple"}
-- 返回 table 连接后的字符串
print("连接后的字符串", table.concat(fruits))
-- 指定连接字符
print("连接后的字符串 ", table.concat(fruits, ", "))
-- 指定索引来连接 table
print("连接后的字符串", table.concat(fruits, "-", 2, 3))

--插入和移除
--以下实例演示了 table 的插入和移除操作:
-- 在末尾插入
table.insert(fruits, "mango")
print("索引为4的元素为", fruits[4])

--在索引为2的键处插入
table.insert(fruits, 2, "grapes")
print("索引为 2 的元素为 ", fruits[2])
print("最后一个元素为 ", fruits[5])
table.remove(fruits)
print("移除后最后一个元素为 ", fruits[5])

--Table 排序
--以下实例演示了 sort() 方法的使用，用于对 Table 进行排序：
fruits = {"banana", "orange", "apple", "grapes"}
print("排序前")
for k, v in ipairs(fruits) do
    print(k, v)
end

table.sort(fruits)
print("排序后")
for k, v in ipairs(fruits) do
    print(k, v)
end

--Table 最大值
--table.maxn 在 Lua5.2 之后该方法已经不存在了，我们定义了 table_maxn 方法来实现。
--以下实例演示了如何获取 table 中的最大值：
function table_maxn(t)
    local mn = nil;
    for k, v in pairs(t) do
        if(mn == nil) then
            mn = v
        end
        if mn < v then
            mn = v
        end 
    end
    print("xxxxxx", mn)
    return mn
end

tbl = {[1] = 2, [2] = 6, [3] = 34, [26] = 5}
print("tbl最大值", table_maxn(tbl))
print("tbl长度", #tbl)

--注意：
--当我们获取 table 的长度的时候无论是使用 # 还是 table.getn 其都会在索引中断的地方停止计数，而导致无法正确取得 table 的长度。
--可以使用以下方法来代替：
function table_leng(t)
    local leng = 0
    for k, v in pairs(t) do
        leng = leng + 1
    end
    return leng
end

print("tbl长度1", table_leng(tbl))


--table 去重
function table.unique(t, bArray)
    local check = {}
    local n = {}
    local idx = 1
    for k, v in pairs(t) do
        if not check[v] then
            if bArray then
                n[idx] = v
                idx = idx + 1
            else
                n[k] = v
            end
        end
    end
    return n
end


--测试
arr = {1,1,1,2,4,5,3,2,5,3,6}
for v in table.unique(arr, nil) do
    print(v)
end
