# -*- coding: utf-8 -*-
# Project : web-framework
# Created by igor on 16/9/21

import logging
import asyncio

from framework.http_utils import Request, Response
from framework.exceptions import BadRequestException, NotFoundException

TIMEOUT = 5


class HTTPServer(object):
    '''
    Contains objects that are shared by HTTPConnections and schedules async
    connections

    Each instance of HTTPServer can listen on one port
    '''

    def __init__(self, router, http_parser, loop):
        '''
        :param router:An object that must expose the 'get_handler' interface
        :param http_parser: An object that must expose the 'parse_into' interface,
        which works with a Request object and a bytearray
        :param loop: An object that implements the 'asyncio.BaseEventLoop' interface
        '''
        self.router = router
        self.http_parser = http_parser
        self.loop = loop

    async def handle_connection(self, reader, writer):
        '''
        Creates and schedules a HTTPConnection given a set(reader,writer) objects
        passed to asyncio.start_server and serves as a callbacks
        :param reader: An object that implements the 'asyncio.StreamReader' interface
        :param writer: An object that implements the 'asyncio.StreamWriter' interface
        :return:
        '''
        connection = HTTPConnection(self, reader, writer)
        asyncio.ensure_future(connection.handle_request(), loop=self.loop)


class HTTPConnection(object):
    '''
    Takes care of whole life cycle of a single TCP connection with a
    HTTP client. First reads incoming data, parses it with
    'http_server.parser',generates as Response with 'http_server.router'
    and sends data back to client
    '''

    def __init__(self, http_server, reader, writer):
        '''

        :param http_server: An instance of HTTPServer
        :param reader: An object that implements the 'asyncio.StreamReader' interface
        :param writer: An object that implements the 'asyncio.StreamWriter' interface
        '''
        self.router = http_server.router
        self.http_parser = http_server.http_parser
        self.loop = http_server.loop

        self._reader = reader
        self._writer = writer
        self._buffer = bytearray()
        self._conn_timeout = None
        self.request = Request()

    async def handle_request(self):
        '''
        Reads bytes from a connection and attempts to parse them
        incrementally until it can issue a Response and close the
        connection.
        Also handles resetting the timeout counter for a connection
        :return:
        '''
        try:
            while not self.request.finished and not self._reader.at_eof():  # 循环的接受请求内容
                data = await self._reader.read(1024)
                if data:
                    self._reset_conn_timeout()
                    await self.process_data(data)
            if self.request.finished:
                await self.reply()
            elif self._reader.at_eof():
                raise BadRequestException()
        except (NotFoundException, BadRequestException) as e:
            self.error_reply(e.code, body=Response.reason_phrases[e.code])
        except Exception as e:
            logging.error(e)
            logging.error(e.__traceback__)
            self.error_reply(500, body=Response.reason_phrases[500])

        self.close_connection()

    async def process_data(self, data):
        '''
        Accumulates data inside of _buffer and attempts to
        parse the accumulated data
        :param data: a bytearray object
        :return:
        '''
        self._buffer.extend(data)
        self._buffer = self.http_parser.parse_into(
            self.request, self._buffer)

    async def reply(self):
        '''
        Obtains and apllies the correct handler from 'self.router'
        and write the Response back to the client
        :return:
        '''

        logging.debug("Replying to request")
        request = self.request
        handler = self.router.get_handler(request.path)  # Dependency injection

        response = await handler.handle(request)

        if not isinstance(response, Response):
            response = Response(code=200, body=response)

        self._writer.write(response.to_bytes())
        await self._writer.drain()

    def close_connection(self):
        '''
        Cancels the timeout timer and closes the connection
        '''
        self._cancel_conn_timeout()
        self._writer.close()

    def _conn_timeout_close(self):
        self.error_reply(500, 'timeout')
        self.close_connection()

    def _cancel_conn_timeout(self):
        if self._conn_timeout:
            self._conn_timeout.cancel()

    def _reset_conn_timeout(self, timeout=TIMEOUT):
        self._cancel_conn_timeout()
        self._conn_timeout = self.loop.call_later(
            timeout, self._conn_timeout_close)

    def error_reply(self, code, body=''):
        '''
        Generates a simple error response
        :param code: Integer singifying the HTTP error.
        :param body: A string that contains an error message.
        :return:
        '''
        response = Response(code=code, body=body)
        self._writer.write(response.to_bytes())
        self._writer.drain()
