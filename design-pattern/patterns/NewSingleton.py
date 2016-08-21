# -*- coding: utf-8 -*-
# Project : design-pattern
# Created by igor on 16/8/21
'''
use __new__ implement Singleton
'''


class OnlyOne(object):
    class __OnlyOne:
        def __init__(self):
            self.val = None

        def __str__(self):
            return repr(self) + self.val

    instance = None

    def __new__(cls):
        if not OnlyOne.instance:
            OnlyOne.instance = OnlyOne.__OnlyOne()
        return OnlyOne.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)


x = OnlyOne()
x.val = "first"
y = OnlyOne()
y.val = "second"
z = OnlyOne()
z.val = "third"
