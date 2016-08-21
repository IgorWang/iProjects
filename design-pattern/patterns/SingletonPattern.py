# -*- coding: utf-8 -*-
# Project : design-pattern
# Created by igor on 16/8/21

class OnlyOne:
    class __OnlyOne:
        def __init__(self, arg):
            self.val = arg

        def __str__(self):
            return repr(self) + self.val

    instance = None

    def __init__(self, arg):
        if not OnlyOne.instance:
            OnlyOne.instance = OnlyOne.__OnlyOne(arg)
        else:
            OnlyOne.instance.val = arg

    def __getattr__(self, item):  # 用__getattr__方法访问属性
        return getattr(self.instance, item)


if __name__ == '__main__':
    # unit test
    x = OnlyOne("first instance")
    print(x)
    y = OnlyOne("second instance")
    print(y)
    z = OnlyOne("third instance")
    print(z)
