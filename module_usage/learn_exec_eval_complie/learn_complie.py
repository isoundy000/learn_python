# -*- encoding: utf-8 -*-
'''
Created on 2019年11月11日

@author: houguangdong
'''
s = """              #一大段代码
for x in range(10):
    print x 
"""
code_exec = compile(s, '<string>', 'exec')   #必须要指定mode，指定错了和不指定就会报错。
code_eval = compile('10 + 20', '<string>', 'eval')   #单个表达式
code_single = compile('name = input("Input Your Name: ")', '<string>', 'single')   #交互式

exec ('print code_exec')       # 使用的exec，因此没有返回值
b = eval(code_eval)

exec ('print code_single')     # 交互
d = eval(code_single)

# Input Your Name: 2222
print('b: ', b)
print('name: ', name)
print('d: ', d)
print('name; ', name)




# s = """              #一大段代码
# for x in range(10):
#     print(x, end='')
# print()
# """
# code_exec = compile(s, '<string>', 'exec')   #必须要指定mode，指定错了和不指定就会报错。
# code_eval = compile('10 + 20', '<string>', 'eval')   #单个表达式
# code_single = compile('name = input("Input Your Name: ")', '<string>', 'single')   #交互式
#
# a = exec(code_exec)   使用的exec，因此没有返回值
# b = eval(code_eval)
#
# c = exec(code_single)  交互
# d = eval(code_single)
#
# print('a: ', a)
# print('b: ', b)
# print('c: ', c)
# print('name: ', name)
# print('d: ', d)
# print('name; ', name)