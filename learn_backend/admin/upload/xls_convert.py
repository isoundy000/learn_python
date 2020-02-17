#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import itertools
import traceback

from lib.utils.debug import print_log
from admin.upload import config_templates as CT


def unicode_int_list(x):
    """# unicode_int_list: docstring
    args:
        x:    ---    arg
    returns:
        0    ---
    """
    l = x.split('],')
    r_l = []
    for ll in l:
        if not ll:
            continue
        ll = ll.strip(' ').replace(']', '').replace('[', '')
        llll = ll.split(',')
        try:
            r_l.append("""[unicode('''%s''', 'utf-8'), %s, %s]""" % tuple(llll))
        except:
            raise KeyError, str(llll) + ll
    return '[' + ','.join(r_l) + ']'


def adv_str(x):
    try:
        return """'%s'""" % str(int(x))
    except ValueError:
        return """'%s'""" % str(x)

def adv_int_list(x):
    try:
        x = str(int(x))
    except ValueError:
        x = x
    except TypeError:
        x = x
    return """[%s]""" % x if x not in [None, '[]', '0', '0.0', 0, 0.0] else """[]"""


def adv_unicode_int_list(x):
    ss = x.replace(' ', '').lstrip('[').rstrip(']')
    l = ss.split('],[')
    r = []
    for i in l:
        rr = [ii if ii.replace('.', '').isdigit() else 'unicode("""%s""", "utf-8")' % ii for ii in i.split(',')]
        r.append('[' + ', '.join(rr) + ']')
    return '[' + ', '.join(r) + ']'


def adv_str_int_list(x):
    if not x: return '[]'
    ss = x.replace(' ', '').rstrip(',').lstrip('[').rstrip(']')
    l = ss.split('],[')
    r = []
    for i in l:
        rr = [ii if ii.replace('.', '').isdigit() else 'str("""%s""")' % ii for ii in i.split(',')]
        r.append('[' + ', '.join(rr) + ']')
    return '[' + ', '.join(r) + ']'


def adv_unicode_list(x):
    ss = x.replace(' ', '').lstrip('[').rstrip(']')
    l = ss.split('],[')
    r = []
    for i in l:
        rr = ['unicode("""%s""", "utf-8")' % ii for ii in i.split(',')]
        r.append('[' + ', '.join(rr) + ']')
    return '[' + ', '.join(r) + ']'


mapping = {
    "int": lambda x: int(x) if x else 0,
    "float": lambda x: float(x) if x not in ['', None] else 0.0,
    "str": lambda x: adv_str(x) if x is not None else """''""",
    "str_list": lambda x: str([str(i) for i in x.split(',')]) if x is not None else """[]""",
    "unicode": lambda x: """unicode('''%s''', 'utf-8')""" % x if x is not None else """''""",
    "bool": lambda x: """%s""" % bool(x) if x is not None else """False""",
    "int_single_list": lambda x: [int(i) for i in eval("""[%s]""" % x)] if x is not None else """[]""",  # 只有一层的数据结构 eg:[1, 2]
    "int_list": adv_int_list,       # 可能有多层的数据结构 eg:[1, [2, 3], 4]
    "unicode_int_list": lambda x: adv_unicode_int_list(x) if x is not None else """[]""",
    "adv_str_int_list": lambda x: adv_str_int_list(x) if x is not None else '[]',
    "unicode_list": lambda x: adv_unicode_list(x) if x is not None else """[]""",
}


def to_pyobj(s):
    """# to_pyobj: docstring
    args:
        s:    ---    arg
    returns:
        0    ---
    """
    r = []
    keys = []
    iter_r = s.iter_rows()
    for i, row in enumerate(iter_r):
        if i in [0]:
            for c in row:
                keys.append(c.internal_value)
            continue
        if not row[0].internal_value and row[0].internal_value != 0: break
        is_None = True
        d = {}
        d['order'] = i  # 排序
        for k, v in itertools.izip(keys, row):
            if v.internal_value:
                is_None = False
            d[k] = v.internal_value
        if is_None:
            continue
        r.append(d)
    return r


def to_config_string(config_name, data):
    """# to_config_string: docstring
    args:
        data:    ---    arg
    returns:
        0    ---
    """
    template_tuple = getattr(CT, config_name)()
    if len(template_tuple) == 2:
        trans, funcs = template_tuple
    elif len(template_tuple) == 3:
        trans, funcs, check_func_list = template_tuple
    else:
        raise TypeError("to_config_string takes 2 or 3 arguments, (%s)")

    r = []
    for line_no, line in enumerate(data):
        for tran in trans:
            if len(tran) == 3:
                tran_col_name, tran_format, tran_type = tran
                tran_check = None
            else:
                tran_col_name, tran_format, tran_type, tran_check = tran
            tran_check = None
            # if tran_col_name != 'END' and tran_col_name not in line:
            #     continue
            tran_format = tran_format.replace(' ', '')
            if tran_type == 'None':     # 结束标记
                s = tran_format
            elif isinstance(tran_type, tuple):  # 类型为元祖的
                l = []
                try:
                    for i in xrange(len(tran_type)):
                        if isinstance(tran_col_name, tuple):
                            value = line[tran_col_name[i]]
                        else:
                            value = line[tran_col_name + '_' + str(i)]
                        tran_data = mapping[tran_type[i]](value)
                        if tran_check is not None and tran_check[i] is not None:
                            flag = tran_check[i](eval(tran_data))
                            if not flag:
                                raise KeyError("line_no=", line_no, "msg=", tran_data)
                        l.append(tran_data)

                    s = tran_format % tuple(l)
                except Exception, e:
                    print_log(tran_format, config_name, l)
                    etype, value, tb = sys.exc_info()
                    line = traceback.format_exception_only(etype, value)
                    raise KeyError("line_no=", line_no, "msg=", line)
            else:
                value = line[tran_col_name]
                try:
                    tran_data = mapping[tran_type](value)
                    if tran_check is not None:
                        check_args = eval(tran_data) if isinstance(tran_data, basestring) else tran_data
                        flag = tran_check(check_args)
                        if not flag:
                            raise KeyError("line_no=", line_no, "msg=", tran_data)
                    s = tran_format % tran_data
                except Exception, e:
                    print_log('lineno: ', line_no, tran_format, config_name, repr(value))
                    print_log('format_exc: ', traceback.format_exc())
                    etype, value, tb = sys.exc_info()
                    line = traceback.format_exception_only(etype, value)
                    raise KeyError("line_no=", line_no, "msg=", line)
            if funcs.get(tran_col_name, lambda x: True)(s):
                r.append(s)
    return '{\n' + '\n'.join(r) + '\n}'