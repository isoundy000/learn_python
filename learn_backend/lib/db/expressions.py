#!/usr/bin/env python
# -*- coding:utf-8 -*-


class Incr(object):

    def __init__(self, key, value, field):
        self.key = key
        self.value = value
        self.field = field

    def to_insert(self):
        return self.value

    def to_update(self):
        self.field.reload_cache = True
        return "`%s` + %d" % (self.key, self.value)

    def __call__(self):
        pass


if __name__ == '__main__':
    import ujson
    incr = Incr(1, 2, 3)

    print dir(incr)

    print ujson.dumps(incr)