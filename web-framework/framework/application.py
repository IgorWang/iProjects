# -*- coding: utf-8 -*-
# Project : web-framework
# Created by igor on 16/9/24
import asyncio
import logging
import re

from framework.exceptions import DiyFrameworkException, NotFoundException, DuplicateRoute
from framework import http_parser
from framework.http_server import HTTPServer

logger = logging.getLogger(__name__)
basic_logger_config = {
    'format': '%(asctime)s [%(levelname)s] %(message)s',
    'level': logging.INFO,
    'filename': None
}

logging.basicConfig(**basic_logger_config)


class App(object):
    '''
    Contains the configuration needed to handle HTTP requests.
    '''

    def __init__(self,
                 router,
                 host='127.0.0.1',
                 port='8080',
                 log_level=logging.INFO,
                 http_parser=http_parser):
        '''

        :param router:a collection of routes that implement the 'get_handler' interface
        :param host: a string that represents and ipv4 address associated
            with the interface that will listen for incoming connections
        :param port: an int that represents the port on which to listen to
        :param log_level: logging level
        :param http_parser: an object that implement 'parse_into' interface.
            Responsible for parsing bytes into Requests object
        '''
        self.router = router
        self.http_parser = http_parser
        self.host = host
        self.port = port
        self._server = None
        self._connection_handler = None
        self._loop = None

        logger.setLevel(log_level)

    def start_server(self):
        '''
        Starts listening asynchronously for TCP connection on a sockets and
        passes each connection to the HTTPServer.handle_connection method
        '''
        if not self._server:
            self._loop = asyncio.get_event_loop()
            self._server = HTTPServer(self.router, self.http_parser, self._loop)
            self._connection_handler = asyncio.start_server(
                self._server.handle_connection,
                host=self.host,
                port=self.port,
                reuse_address=True,
                reuse_port=True,
                loop=self._loop)

            logger.info("Starting server on {0}:{1}".format(
                self.host, self.port))
            self._loop.run_until_complete(self._connection_handler)

            try:
                self._loop.run_forever()
            except KeyboardInterrupt:
                logger.info('Got signal, killing server')
            except DiyFrameworkException as e:
                logger.error('Critical framework failure:')
                logger.error(e.__traceback__)
            finally:
                self._loop.close()
        else:
            logger.info('Server already started - {0}'.format(self))

    def __repr__(self):
        cls = self.__class__
        if self._connection_handler:
            return '{0} - Listening on: {1}:{2}'.format(
                cls, self.host, self.port)
        else:
            return '{0} - Not started'.format(cls)


class HandleWrapper(object):
    '''
    Helper class that calls a user defined handler with a Request as the first
    argument and route defined parameters as kwargs
    '''

    def __init__(self, handler, path_params):
        self.handler = handler
        self.path_params = path_params
        self.request = None

    async def handle(self, request):
        return await self.handler(request, **self.path_params)


class Router(object):
    '''
    Container used to add and match a group of routes.
    '''

    def __init__(self):
        self.routes = {}

    def add_routes(self, routes):
        for route, fn in routes.items():
            self.add_route(route, fn)

    def add_route(self, path, handler):
        '''
        Creates a path:function pair for later retrieval by path.The
        path is turned into a regular expression.

        :param path: A string that matches a URL path
        :param handler: An async function that accepts a request and
            return a string or Response object.
        '''
        compiled_route = self.__class__.build_route_regexp(path)
        if compiled_route not in self.routes:
            self.routes[compiled_route] = handler
        else:
            raise DuplicateRoute

    def get_handler(self, path):
        '''
        Retrieves the correct async function to proess a request

        :param path: path part of an HTTP request
        :return: an function that accepts a request and returns a string or
            Response object
        '''
        logging.debug("Getting handler for: {0}".format(path))
        for route, handler in self.routes.items():
            path_params = self.__class__.match_path(route, path)
            if path_params is not None:
                logger.debug('Got handler for: {0}'.format(path))
                wrapped_handler = HandleWrapper(handler, path_params)
                return wrapped_handler
        raise NotFoundException()

    @classmethod
    def build_route_regexp(cls, regexp_str):
        '''
        Turns a string into a compiled regular expression. Parses '{}' into
        named groups ie. '/path/{variable}' is turned into
        '/path/(?P<variable>[a-zA-Z0-9_-]+)'

        :param regexp_str: a string representing a URL path.
        :return: a comipled regular expression.
        '''

        def named_groups(matchobj):
            return '(?P<{0}>[a-zA-Z0-9_-]+)'.format(matchobj.group(1))

        re_str = re.sub(r'{([a-zA-Z0-9_-]+)}', named_groups, regexp_str)
        re_str = ''.join(('^', re_str, '$',))
        # logger.debug('Compiling "{0}" regexp'.format(re_str))
        return re.compile(re_str)

    @classmethod
    def match_path(cls, route, path):
        '''
        Utility function that returns URL parameters if a path matches a route
        or None if it doesn't

        :param route: a compiled regexp that represents a route
        :param path: a URL path to be matched against the route
        :return: Either a dict of URL param:value pairs if path matches the
            route else None.
        '''
        match = route.match(path)
        try:
            return match.groupdict()
        except AttributeError:
            return
