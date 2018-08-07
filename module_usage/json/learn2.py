# -*- coding: utf-8 -*-
'''
@finish time:2017-09-30
@author；fengjiexyb
序列化的模块比较
'''
import json
import pickle
import shelve


def shelveSerializable():
    '''这种方式在python2.7中会有异常：AttributeError: DbfilenameShelf instance has no attribute '__exit__'
    # 保存数据到student文件
    with shelve.open('student') as db:
        db['name'] = 'Tom'
        db['age'] = 19
        db['hobby'] = ['篮球', '看电影', '弹吉他']
        db['other_info'] = {'sno': 1, 'addr': 'xxxx'}

    # 读取数据
    with shelve.open('student') as db:
        for key, value in db.items():
            print(key, ': ', value)
    '''
    s = shelve.open("test_shelve")
    s["name"] = "DaLian"
    s["neusoft"] = "HHH"
    s.close()

    f = shelve.open("test_shelve")  # 如果上面没有关闭，但是文件存在，就会读取以前的文件，而不是上面的新文件。
    print(f.get("name"))
    print(f.get("neusoft"))

    f["neusoft"] = "sss"            # 可以修改
    f["soft"] = [1,2]               # 可以添加
    print(f.get("neusoft"))
    print(f.get("soft"))
    f["soft"].append(3)             # 但是追加，还是会显示追加前的数据
    print(f.get("soft"))
    f.writeback = True              # 设置回写，也可以在打开文件时设置
    f["soft"].append(4)             # 现在就可以追加了
    print(f.get("soft"))


'''pickle序列化'''
def pickleSerializable():
    # 序列化
    li = [1, 2, 3, 4, 5]
    pw = open('pickleSerializable', 'wb')
    pw.write(pickle.dumps(li))
    pw.close()

    # 反序列化
    li = json.load(open("pickleSerializable", "r"))
    print(li, type(li))


'''json序列化'''
def jsonSerializable():
    dic = {'k1': 'v1'}
    print(dic, type(dic))
    # json.dumps 把python的基本数据类型转换成字符串形式
    result = json.dumps(dic)
    print(dic, type(result))

    # 反序列化
    s1 = '{"k1":123}'
    # json.loads 把字符串形式转换成其他基本数据类型
    # 注意： 反序列化时，中间字符串一定用""表示，原因：跨语言操作时，其他语言是用""表示字符串
    dic1 = json.loads(s1)
    print(dic1, type(dic1))

    # 序列化并把内容写进文本
    # 也可以写成pickle例子的形式
    li = [1, 2, 3, 4, 5]
    json.dump(li, open("test", "w"))

    # 从文本读出字符串并进行反序列化，但文件中的内容只能有一个基本数据
    li = json.load(open("test", "r"))
    print(li, type(li))


def main():
    shelveSerializable()


if __name__ == "__main__":
    main()