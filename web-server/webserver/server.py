# -*- coding: utf-8 -*-
# Project : web-server
# Created by igor on 16/8/6
import os, sys, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer


class ServerException(Exception):
    '''
    服务器内部错误
    '''
    pass


class Case_no_file(object):
    '''路径不存在'''

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class Case_existing_file(object):
    '''文件存在'''

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path)


class Case_always_fail(object):
    '''所有情况都不符合的默认处理类'''

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknow object '{0}'".format(handler.path))


class Case_directory_index_file(object):
    def index_path(self, handler):
        return os.path.join(handler.full_path,
                            'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler))


class Case_cgi_file(object):
    '''
    脚本文件处理
    '''

    def test(self, handler):
        return os.path.isfile(handler.full_path) and handler.full_path.endswith('.py')

    def act(self, handler):
        ## 运行脚本
        handler.run_cgi(handler.full_path)


class RequestHandler(BaseHTTPRequestHandler):
    '''处理请求并返回指定的页面'''

    # 页面模版
    Page = '''
    <html>
    <body>
    <table>
    <tr> <td>Header</td>        <td><Value></td>        </tr>
    <tr> <td>Date and time</td> <td>{date_time}</td>    </tr>
    <tr> <td>Client host</td>   <td>{client_host}</td>  </tr>
    <tr> <td>Client port</td>   <td>{client_port}</td>  </tr>
    <tr> <td>Command</td>       <td>{command}</td>      </tr>
    <tr> <td>Path</td>          <td>{path}</td>         </tr>
    </table>
    </body>
    </html>
    '''

    # 错误页
    Error_Page = '''
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    '''

    Cases = [Case_no_file(),
             Case_cgi_file(),
             Case_existing_file(),
             Case_directory_index_file(),
             Case_always_fail()]

    # 处理一个GET请求
    def do_GET(self):
        try:
            self.full_path = os.getcwd() + self.path
            for case in self.Cases:
                handler = case
                # 如果满足该类的情况
                if handler.test(self):
                    handler.act(self)
                    break

        except Exception as msg:
            self.handle_error(msg)

        page = self.create_page()
        self.send_content(page)

    def create_page(self):
        values = {
            'date_time': self.date_time_string(),
            'client_host': self.client_address[0],
            'client_port': self.client_address[1],
            'command': self.command,
            'path': self.path
        }
        page = self.Page.format(**values)
        return page

    def send_content(self, page, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        if isinstance(page, str):
            page = page.encode()
        self.wfile.write(page)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read : {1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path,
                                         msg=msg)
        self.send_content(content, status=404)

    def run_cgi(self, full_path):
        data = subprocess.check_output(["python", full_path])
        self.send_content(data)


if __name__ == "__main__":
    serverAddress = ("", 8080)
    server = HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
