#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghou'

"""
修改unittest的TestCase.failUnlessEqual方法，优化错误的输出
输出对比：

之前：
======================================================================
FAIL: # get_info: 获取最新信息
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/laonger/Documents/Work/REKOO/mixi_town_pc/test/test/unit/test_wharf.py", line 684, in test_get_info
    %(str(test_result), str(result))
  File "/Users/laonger/Documents/Work/REKOO/mixi_town_pc/test/test/unittest_pro.py", line 32, in failUnlessEqual
    raise self.failureException, msg
AssertionError: 
                error test_result != result, 
                test_result:{'employee': [{}, {'image': 'baixiaolin.png', 'uid': '25549535', 'name': u'\u767d\u6653\u6797'}, {'image': 'sunny.png', 'uid': 'sunny', 'name': u'\u6332\u5c3c'}], 'boats': {'0': {'category': 'fanchuan', 'status': 'sailing', 'out_time': 1310467420957.9729, 'back_time': 1310467540958.9729}}, 'dock_boat': {'0': '0'}, 'level': 1}, 
                result:{'employee': [{}, {'image': 'baixiaolin.png', 'uid': '25549535', 'name': u'\u767d\u6653\u6797'}, {'image': 'sunny.png', 'uid': 'sunny', 'name': u'\u6332\u5c3c'}], 'boats': {'0': {'category': 'fanchuan', 'status': 'sailing', 'out_time': 1310467420957.9729, 'back_time': 1310467540957.9729}}, 'dock_boat': {'0': '0'}, 'level': 1}


之后：
======================================================================
FAIL: # dict: docstring
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/laonger/Documents/Work/REKOO/mixi_town_pc/test/test/unit/test_wharf.py", line 795, in test_dict
    self.assertEqual(d, d1, msg=None, first_name='d', second_name='d1')
  File "/Users/laonger/Documents/Work/REKOO/mixi_town_pc/test/test/unittest_pro.py", line 32, in failUnlessEqual
    raise self.failureException, msg
AssertionError: 
    error d != d1, 
    d: -, 
    d1: +, 
  {'0': {'back_time': 0,
         'category': 'qiting',
         'out_time': 0,
-        'status': 'docking'},
+        'status': 'docking1'},
?                          +

   '1': {'back_time': 0,
         'category': 'qiting',
         'out_time': 0,
-        'status': 'docking'},
+        'status': 'docking1'},
?                          +

   '2': {'back_time': 0,
         'category': 'qiting',
         'out_time': 0,
-        'status': 'docking'},
+        'status': 'docking1'},
?                          +

   '3': {'back_time': 0,
         'category': 'qiting',
         'out_time': 0,
-        'status': 'docking'},
+        'status': 'docking1'},
?                          +

   '4': {'back_time': 0,
         'category': 'qiting',
         'out_time': 0,
-        'status': 'docking'}}
+        'status': 'docking1'}}
?                          +

"""

import pprint
import difflib
import unittest


class TestCase(unittest.TestCase):
    """# TestCase: docstring"""
    def __init__(self, methodName='runTest'):
        super(TestCase, self).__init__(methodName)

    def failUnlessEqual(self, first, second, msg=None, first_name='first', second_name='second'):
        """# failUnlessEqual: docstring
        args:
            first, second, msg=None:    ---    arg
        returns:
            0    ---
        """
        if not first == second:
            if not msg:
                first_str = pprint.pformat(first).splitlines()
                second_str = pprint.pformat(second).splitlines()
                diff = difflib.ndiff(first_str, second_str)
                # diff = difflib.context_diff(pprint.pformat(first).splitlines(),
                #              pprint.pformat(second).splitlines())
                msg = '''\n    error %s != %s, \n    -: %s, \n    +: %s, \n%s''' % (
                    first_name,
                    second_name,
                    first_name,
                    second_name,
                    '\n'.join(diff)
                )

            raise self.failureException, msg

    assertEquals = assertEquals = failUnlessEqual


__all__ = unittest.__all__
g = globals()
for a in __all__:
    if a == 'TestCase':
        continue
    g[a] = getattr(unittest, a)