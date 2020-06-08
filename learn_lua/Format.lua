#!/usr/local/bin/lua

string1 = "Lua"
string2 = "Tutorial"

number1 = 10
number2 = 20

-- 基本字符串格式化
print(string.format("基本格式化 %s %s", string1, string2))
-- 日期格式化
date = 2; month = 1; year = 2014
print(string.format("日期格式化 %02d/%02d/%03d", date, month, year))
-- 十进制格式化
print(string.format("%.4f", 1/3))
print(string.format("%c", 83))
print(string.format("%+d", 17.0))
print(string.format("%05d", 17))           --    输出00017
print(string.format("%o", 17))             --    输出21
print("=========")
print(string.format("%u", 3))              --    输出3
print("-----------")
print(string.format("%x", 13))             --    输出d
print(string.format("%X", 13))             --    输出D
print(string.format("%e", 1000))           --    输出1.000000e+03
print(string.format("%E", 1000))           --    输出1.000000E+03
print(string.format("%6.3f", 13))          --    输出13.000
print(string.format("%q", "One\nTwo"))     --    输出"OneTwo"
print(string.format("%s", "monkey"))       --    输出monkey
print(string.format("%10s", "monkey"))     --    输出    monkey
print(string.format("%5.3s", "monkey"))    --    输出  mon



print(string.byte("Lua"))
print(string.byte("Lua", 3))
print(string.byte("Lua", -1))
print(string.byte("Lua", -2))
print(string.byte("Lua", 2))
print(string.char(97))


string1 = "www."
string2 = "runoob"
string3 = ".com"
--使用..进行字符串链接
print("链接字符串", string1..string2..string3)
--字符串长度
print("字符串长度", string.len(string2))
repeatedString = string.rep(string2, 2)
print(repeatedString)
s = "Deadline is 30/05/1999, firm"
date = "%d%d/%d%d/%d%d%d%d"
print(string.find(s, date))
print("--------------------")
print(string.sub(s, string.find(s, date)))
print("====================")
print(string.gsub("hello, up-down!", "%A", "."))


--将阿拉伯数字转换为语文汉字数字：
local function NumToCN(num)
    local size = #tostring(num)
    local CN = ""
    local StrCN = {"一","二","三","四","五","六","七","八","九"}
    for i=1, size do
    	CN = CN .. StrCN[tonumber(string.sub(tostring(num), i, i))]
    end
    return CN
end

print(NumToCN(56665))

--移除中文部分：
function StrSplit(inputstr, sep)
    if sep == nil then
        sep = "%s"
    end
    local t = {}
    local i = 1
    print("([^"..sep.."]+)")
    print('**************')
    for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
    	t[i] = str
        i = i + 1
    end
    return t
end

local a = "23245023496830,汉字。。。。"
local b = ":"
b = StrSplit(a, ",")
print(#b)
print(b[1])
print(b[2])

--去除字符串首尾的空格
function trim(s)
    return (string.gsub(s, "^%s*(.-)%s*$", "%1"))
end
string1 = "   RUNOOB        "
string2 = trim(string1)
print(string2)
