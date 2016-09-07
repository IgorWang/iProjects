# -*- coding: utf-8 -*-
# Project : design-pattern
# Created by igor on 16/9/7

class A(object):
    pass


if __name__ == '__main__':
    a = A()
    b = A()
    print(id(a) == id(b))
    print(a, b)
