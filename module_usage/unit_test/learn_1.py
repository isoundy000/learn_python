# -*- encoding: utf-8 -*-
'''
Created on 2017年8月29日

@author: houguangdong
'''

import unittest
for item in dir(unittest):
    cur = getattr(unittest, item)
#     print help(cur)
    
# 2、通过testsuit来执行测试用例的方式：
# 执行测试的类
class UCTestCase(unittest.TestCase):
    def setUp(self):
        #测试前需执行的操作
        pass
    
    def tearDown(self):
        #测试用例执行完后所需执行的操作
        pass
    
    # 测试用例1
    def testCreateFolder(self):
        #具体的测试脚本
        self.assertEqual(1, 1, "1111111")
        
    # 测试用例2
    def testDeleteFolder(self):
        #具体的测试脚本
        self.assertEqual(2, 2, "2222222")
        
    # 有时希望某些用例不被执行，unittest.skip() 提供了忽略某个测试用例的功能，用法如下：
    @unittest.skip('skip is upper.')
    def testIsupper(self):
        self.assertEqual(3, 3, "3333333")
        
        
# 3、通过testLoader方式：
class TestCase1(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testCase1(self):
        print 'aaa'      
    
    def testCase2(self):
        print 'bbb'
        

class TestCase2(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testCase1(self):
        print 'aaa1'  
    
    def testCase2(self):
        print 'bbb1'
    

if __name__ == "__main__":
    unittest.main()
    # 构造测试集
    suite = unittest.TestSuite()
    suite.addTest(UCTestCase("testCreateFolder"))
    suite.addTest(UCTestCase("testDeleteFolder"))
    # 执行测试
    runner = unittest.TextTestRunner()
    runner.run(suite)
    
    # 此用法可以同时测试多个类
    suite1 = unittest.TestLoader().loadTestsFromTestCase(TestCase1) 
    suite2 = unittest.TestLoader().loadTestsFromTestCase(TestCase2) 
    suite = unittest.TestSuite([suite1, suite2]) 
    unittest.TextTestRunner(verbosity=2).run(suite)


# 查看所有的命令行选项使用命令
# python -m unittest -h

# unittest 提供了丰富的命令行入口，可以根据需要执行某些特定的用例。有了命令行的支持，上述例子的最后两行代码就显得冗余，应当被移除：
# 执行 testdemo.py 文件所有的测试用例：
# python -m unittest testdemo

# 执行 testdemo.py 文件的 TestStringMethods 类的所有测试用例：
# python -m unittest test_demo.TestStringMethods

# 执行 testdemo.py 文件 TestStringMethods 类的 test_upper：
# python -m unittest test_demo.TestStringMethods.test_upper

# unittest 提供了自动匹配发现并执行测试用例的功能，随着项目代码结构越发庞大，势必有多个测试文件，自动匹配发现并测试用例的功能在此就显得非常有用，只要满足 load_tests protocol 的测试用例都会被 unittest 发现并执行，测试用例文件的默认匹配规则为 test*.py。通过一条命令即可执行所有的测试用例，如此就很容易被 tox 等测试工具所集成。使用如下：
# python -m unittest discover
# 参数如下：
# -v, --verbose
# Verbose output

# -s, --start-directory directory
# Directory to start discovery (. default)

# -p, --pattern pattern
# Pattern to match test files (test*.py default)

# -t, --top-level-directory directory
# Top level directory of project (defaults to start directory)

# 假设现在要被测试的代码目录如下：
# $ tree demo
# demo
# ├── testdemo.py
# └── testdemo1.py

# $ python -m unittest discover -s demo -v
# test_isupper (testdemo.TestStringMethods) ... ok
# test_upper (testdemo.TestStringMethods) ... ok
# test_is_not_prime (testdemo1.TestPrimerMethods) ... ok
# test_is_prime (testdemo1.TestPrimerMethods) ... ok

# A Collection of Assertion
# +--------------------------------+-------------------------------------------------------+-------+
# | Method                         |Checks that                                            |New in |
# +--------------------------------+-------------------------------------------------------+-------+
# | assertEqual(a, b)              | a == b                                                |       |
# | assertNotEqual(a, b)           | a != b                                                |       |
# | assertTrue(x)                  | bool(x) is True                                       |       |
# | assertFalse(x)                 | bool(x) is False                                      |       |
# | assertIs(a, b)                 | a is b                                                | 2.7   |
# | assertIsNot(a, b)              | a is not b                                            | 2.7   |
# | assertIsNone(x)                | x is None                                             | 2.7   |
# | assertIsNotNone(x)             | x is not None                                         | 2.7   |
# | assertIn(a, b)                 | a in b                                                | 2.7   |
# | assertNotIn(a, b)              | a not in b                                            | 2.7   |
# | assertIsInstance(a, b)         | isinstance(a, b)                                      | 2.7   |
# | assertNotIsInstance(a, b)      | not isinstance(a, b)                                  | 2.7   |
# | assertAlmostEqual(a, b)        | round(a-b, 7) == 0                                    |       |
# | assertNotAlmostEqual(a, b)     | round(a-b, 7) != 0                                    |       |
# | assertGreater(a, b)            | a > b                                                 | 2.7   |
# | assertGreaterEqual(a, b)       | a >= b                                                | 2.7   |
# | assertLess(a, b)               | a < b                                                 | 2.7   |
# | assertLessEqual(a, b)          | a <= b                                                | 2.7   |
# | assertRegexpMatches(s, r)      | r.search(s)                                           | 2.7   |
# | assertNotRegexpMatches(s, r)   | not r.search(s)                                       | 2.7   |
# | assertItemsEqual(a, b)         | sorted(a) == sorted(b) and works with unhashable objs | 2.7   |
# | assertDictContainsSubset(a, b) | all the key/value pairs in a exist in b               | 2.7   |
# | assertMultiLineEqual(a, b)     | strings                                               | 2.7   |
# | assertSequenceEqual(a, b)      | sequences                                             | 2.7   |
# | assertListEqual(a, b)          | lists                                                 | 2.7   |
# | assertTupleEqual(a, b)         | tuples                                                | 2.7   |
# | assertSetEqual(a, b)           | sets or frozensets                                    | 2.7   |
# | assertDictEqual(a, b)          | dicts                                                 | 2.7   |
# +--------------------------------+-------------------------------------------------------+-------+