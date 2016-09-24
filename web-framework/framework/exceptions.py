# -*- coding: utf-8 -*-
# Project : web-framework
# Created by igor on 16/9/22


class DiyFrameworkException(Exception):
    pass


class BadRequestException(DiyFrameworkException):
    code = 400


class NotFoundException(DiyFrameworkException):
    code = 404


class DuplicateRoute(DiyFrameworkException):
    pass


class TimeoutException(DiyFrameworkException):
    code = 500
