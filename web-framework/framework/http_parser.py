# -*- coding: utf-8 -*-
# Project : web-framework
# Created by igor on 16/9/22
'''
Module response for parsing bytes objects into HTTP requests.
All of the function in here operate on byte buffers and modify them
instead of working on copies.

The http_parser module is a group of functions inside because the parser does not need to keep track of state.
Instead, the calling code has to manage a Request object and pass it into the parse_into function along with a
bytearray containing the raw bytes of a request. To this end, the parser modifies both the request object as well
as the bytearray buffer passed to it. The request object gets fuller and fuller while the bytearray buffer gets
emptier and emptier.
'''
import re
import json
from urllib import parse

from framework.exceptions import BadRequestException

CRLF = b'\x0d\x0a'
SEPARATOR = CRLF + CRLF
HTTP_VERSION = b'1.1'
SUPPORTED_METHODS = [
    'GET',
    'POST'
]

REQUEST_LINE_REGEXP = re.compile(br'[a-z]+ [a-z0-9.?_\[\]=&-\\]+ http/%s' %
                                 (HTTP_VERSION), flags=re.IGNORECASE)


def can_parse_request_line(buffer):
    '''
    Uses a regular expression to determine whether buffer contains
    somethin that looks like an HTTP request line.
    :param buffer: a bytes like object
    '''
    return REQUEST_LINE_REGEXP.match(buffer) is not None


def parse_headers(buffer):
    '''
    Parses the buffer and create a dict of header:value.Collapses
    duplicate headers into one.

    :param buffer: a bytes like object
    :return: Dict of headers.
    '''
    headers_end = buffer.index(SEPARATOR)
    headers_iter = (line for line in buffer[:headers_end].split(CRLF) if line)
    headers = {}
    for line in headers_iter:
        header, value = [i.strip() for i in line.strip().split(b':')[:2]]
        headers[header.decode('utf-8')] = value.decode('utf-8')
    return headers


def parse_query_params(raw_path):
    '''
    Parses a string to extract the path and any URL params

    :param raw_path:string representation of an HTTP path ie. /path?key=val.
    :return: path string and a dict of URL params in the form of {key:[val]}
    '''
    url_obj = parse.urlparse(raw_path)
    path = url_obj.path
    query_params = parse.parse_qs(url_obj.query)
    return path, query_params


def parse_request_line(buffer):
    '''
    Parses the buffer to extract information from the request line.

    :param _buffer: a bytes like object
    :return: A type of HTTP method,path,and query params
    '''
    request_line = buffer.split(CRLF)[0].decode('utf-8')  # decode to str
    method, raw_path = request_line.split(" ")[:2]  # you have to know HTTP structure
    method = method.upper()
    if method not in SUPPORTED_METHODS:
        raise BadRequestException('{} method not supported'.format(method))

    path, query_params = parse_query_params(raw_path)
    return method, path, query_params


def remove_request_line(buffer):
    '''
    Deletes the request line from the buffer

    :param buffer: a bytes object
    '''
    first_line_end = buffer.index(CRLF)
    del buffer[:first_line_end]


def can_parse_headers(buffer):
    '''
    Checks to see if buffer contains the CRLFCRFL sequence, with
    signals the end of headers in an HTTP request

    :param buffer:a bytes like object
    '''
    return SEPARATOR in buffer


def has_body(headers):
    '''
    :param headers: A dict-like object
    '''
    return 'content-length' in headers


def remove_intro(buffer):
    '''
    Deletes everything up to the CRLFCRLF sequence - the request
    line as well as the headers.
    :param buffer: a bytes object.
    '''
    request_boundry = buffer.index(SEPARATOR)
    del buffer[:request_boundry + len(SEPARATOR)]

def can_parse_body(headers, buffer):
    '''
    Checks whether a request's headers signal a body to parse.

    :param headers: A dict of header:value pairs.
    :param buffer: a bytes object
    :return: Boolean
    '''
    content_length = int(headers.get('content_length', '0'))
    return 'content-length' in headers and len(buffer) == content_length


def get_body_parser(content_type):
    '''
    Selects the correct parses to use for parsing a request's body.

    :param content_type: a string representing the request's content type.
    :return: function that expects a string input and outputs parsed text.
    '''
    if content_type == 'application/x-wwww-form-urlencoded':
        return parse.parse_qs
    elif content_type == 'application/json':
        return json.dumps


def byte_kv_to_utf8(kv):
    '''
    :param kv: a dict of byte keys:values
    :return: a dict of utf-8 keys:values
    '''
    return {k.decode('utf8'): [val.decode('utf8') for val in v] for k, v in kv.items()}


def parse_body(headers, buffer):
    '''
    Parses a request body according to the Content-Type header.
    Uses application/x-www-form-urlencoded by default.
    :param headers: a dict of header:values pairs
    :param buffer: a bytes of objects.
    :return: A tuple of the raw_body bytes and a parsed, utf-8-encoded,
        dict re[resenting the body
    '''
    body_raw = buffer[:]
    content_type = headers.get('content-type', 'application/x-www-form-urlencoded')
    parser = get_body_parser(content_type)
    body = parser(body_raw)
    utf_8_body = byte_kv_to_utf8(body)
    return body_raw, utf_8_body


def clear_buffer(buffer):
    '''
    Clears the buffer

    :param buffer:a bytes object
    '''
    del buffer[:]


def parse_into(request, buffer):
    '''
    Main function of the module - it incrementally parses a bytes object
    and stores the information in request. First it attempts to parse the
    request line and http headers. Base on that, it then attempts to
    parse the body if applicable. This function expected to be called
    with the same request and buffer objects throughout an HTTP request's
    life cycle

    :param request:an object that will store parsed data.Must expose the
        Request interface.
    :param buffer: a bytes objects. It will copied, the copy will be
        modified during parsing
    :return: A bytes object that is the modified copy of the buffer param.
    '''
    _buffer = buffer[:]
    if not request.method and can_parse_request_line(_buffer):
        (request.method, request.path,
         request.query_params) = parse_request_line(_buffer)
        remove_request_line(_buffer)

    if not request.headers and can_parse_headers(_buffer):
        request.headers = parse_headers(_buffer)
        if not has_body(request.headers):
            request.finished = True
        remove_intro(_buffer)

    if not request.finished and can_parse_body(request.headers, _buffer):
        request.body_raw, request.body = parse_body(request.headers, buffer)
        clear_buffer(_buffer)
        request.finished = True
    return _buffer
