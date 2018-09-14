#!/usr/local/bin/lua
--简单模式
--简单模式使用标准的 I/O 或使用一个当前输入文件和一个当前输出文件。
--以下为 file.lua 文件代码，操作的文件为test.lua(如果没有你需要创建该文件)，代码如下：
-- 以只读方式打开文件
file = io.open("test.lua", "r")

-- 设置默认输入文件为 test.lua
io.input(file)

-- 输出文件第一行
print(io.read())

-- 关闭打开的文件
io.close(file)

-- 以附加的方式打开只写文件
file = io.open("test.lua", "a")

-- 设置默认输出文件为 test.lua
io.output(file)

-- 在文件最后一行添加 Lua 注释
io.write("--  test.lua 文件末尾注释")

-- 关闭打开的文件
io.close(file)