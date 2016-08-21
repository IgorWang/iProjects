# -*- coding: utf-8 -*-
# Project : design-pattern
# Created by igor on 16/8/21
'''
class decorator
'''


class SingletonDecorator:
    def __init__(self, kclass):
        self.kclass = kclass
        self.instance = None

    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = self.kclass(*args, **kwargs)
        return self.instance


if __name__ == '__main__':
    class foo:
        pass


    foo = SingletonDecorator(foo)

    x = foo()
    y = foo()
    z = foo()

    print(x)
    print(y)
    print(z)
