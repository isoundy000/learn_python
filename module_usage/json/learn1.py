# -*- encoding: utf-8 -*-
'''
Created on 2018年8月4日

@author: ghou
'''
import json
# import cPickle as pickle
import pickle
import shelve


class Student(object):

    def __init__(self, name, age, sno):
        self.name = name
        self.age = age
        self.sno = sno

    def __repr__(self):
        return 'Student [name: %s, age: %d, sno: %d]' % (self.name, self.age, self.sno)


stu = Student("Tom", 19, 1)
print stu
print stu.__class__.__name__
print stu.__module__
print stu.__dict__


def obj2dict(obj):
    d = {}
    d['__class__'] = obj.__class__.__name__
    d['__module__'] = obj.__module__
    d.update(obj.__dict__)
    return d


def dict2obj(d):
    if '__class__' in d:
        class_name = d.pop('__class__')
        module_name = d.pop('__module__')
        module = __import__(module_name)
        print module, '111111'
        class_ = getattr(module, class_name)
        args = dict((key.encode('ascii'), value) for key, value in d.items())
        print args
        instance = class_(**args)
    else:
        instance = d
    return instance


print obj2dict(stu)
print json.dumps(obj2dict(stu))
print json.dumps(stu, default=obj2dict)

print json.loads('{"sno": 1, "__module__": "__main__", "age": 19, "__class__": "Student", "name": "Tom"}')
print dict2obj(json.loads('{"sno": 1, "__module__": "__main__", "age": 19, "__class__": "Student", "name": "Tom"}'))
print json.loads('{"sno": 1, "__module__": "__main__", "age": 19, "__class__": "Student", "name": "Tom"}', object_hook=dict2obj)
print '================================'


class MyJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        d = {}
        d['__class__'] = obj.__class__.__name__
        d['__module__'] = obj.__module__
        d.update(obj.__dict__)
        return d


class MyJSONDecoder(json.JSONDecoder):

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict2obj)

    def dict2obj(self, d):
        if '__class__' in d:
            class_name = d.pop('__class__')
            module_name = d.pop('__module__')
            module = __import__(module_name)
            class_ = getattr(module, class_name)
            args = dict((key.encode('ascii'), value) for key, value in d.items())
            instance = class_(**args)
        else:
            instance = d
        return instance


stu1 = Student('HanMeiMei', 20, 1)
print MyJSONEncoder().encode(stu1)
print MyJSONEncoder(separators=(',', ':')).encode(stu1)
print json.dumps(stu1, cls=MyJSONEncoder)
print json.dumps(stu1, cls=MyJSONEncoder, separators=(',', ':'))
print MyJSONDecoder().decode('{"sno": 1, "__module__": "__main__", "age": 20, "__class__": "Student", "name": "HanMeiMei"}')

for chunk in MyJSONEncoder().iterencode(stu1):
    print chunk, '1111'

# bigobject = mysocket = None
# for chunk in MyJSONEncoder().iterencode(bigobject):
#     mysocket.write(chunk)

var_a = {'a': 'str', 'c': True, 'e': 10, 'b': 11.1, 'd': None, 'f': [1, 2, 3], 'g': (4, 5, 6)}
var_b = pickle.dumps(var_a)
print var_b
var_c = pickle.loads(var_b)
print var_c


var_stu = pickle.dumps(stu)
print var_stu
print pickle.loads(var_stu)


db = shelve.open('student')
db['name'] = 'ghou'
db['age'] = 28
db['hobby'] = ['羽毛球', '游泳']
db['other_info'] = {'sno': 1, 'addr': "heilongjiang"}
db.close()


db1 = shelve.open('student')
for key, value in db1.items():
    print key, ":", value
db1.close()