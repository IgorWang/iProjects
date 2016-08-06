# -*- coding: utf-8 -*-
# Project : web-server
# Created by igor on 16/8/6
import BaseHTTPServer, os, sys


class ServerException(Exception):
    '''
    服务器内部错误
    '''
    pass


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
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

    # 处理一个GET请求
    def do_GET(self):
        try:
            full_path = os.getcwd() + self.path
            if not os.path.exists(full_path):
                raise ServerException("'{0} not found ".format(self.path))

            elif os.path.isfile(full_path):
                self.handle_file(full_path)
            else:
                raise ServerException("Unkonw object '{0}'".format(self.path))

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


if __name__ == "__main__":
    serverAddress = ("", 8080)
    server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
