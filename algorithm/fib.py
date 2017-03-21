# -*- encoding: utf-8 -*-
'''
Created on 2017年2月27日

@author: houguangdong
'''

def fib(n):
    a, b = 0, 1
    while a < n:
        print a
        a, b = b, a+b
fib(10)


def recur_fibo(n):
    """递归函数输出斐波那契数列"""
    if n <= 1:
        return n
    else:
        return(recur_fibo(n-1) + recur_fibo(n-2))

# 获取用户输入
input1 = int(input("您要输出几项? "))
# 检查输入的数字是否正确
if input1 <= 0:
    print("输入正数")
else:
    print("斐波那契数列:")
    for i in range(input1):
        print(recur_fibo(i))


def fib(n):
    a,b = 1,1
    for i in range(n-1):
        a,b = b,a+b
    return a
# 输出了第10个斐波那契数列
print fib(10)


def fib(n):
    if n == 1:
        return [1]
    if n == 2:
        return [1, 1]
    fibs = [1, 1]
    for i in range(2, n):
        fibs.append(fibs[-1] + fibs[-2])
    return fibs
# 输出前 10 个斐波那契数列
print fib(10) 