# -*- coding: utf-8 -*-
# Project : design-pattern
# Created by igor on 16/8/21
'''
__dict__
'''


class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class Singleton(Borg):
    def __init__(self, arg):
        Borg.__init__(self)
        self.val = arg

    def __str__(self):
        return self.val

if __name__ == '__main__':
    x = Singleton("first")
    print(repr(x))
    y = Singleton("second")
    print(repr(y))

