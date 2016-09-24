# -*- coding: utf-8 -*-
# Project : web-framework
# Created by igor on 16/9/20

from framework.application import App, Router
from framework.http_utils import Response


# Get simple route
async def home(r):
    rsp = Response()
    rsp.set_header("Content-Type", "text/html")
    rsp.body = "<html><body><b>test</b></body></html>"
    return rsp


# GET route + params
async def welcome(r, name):
    return "Wellcome {}".format(name)


# POST route + body param
async def parse_form(r):
    if r.method == "GET":
        return "form"
    else:
        name = r.body.get('name', '')[0]
        password = r.body.get('password', '')[0]
    return "{0}:{1}".format(name, password)


# application  = router + http server

router = Router()
router.add_routes({
    r'/welcome/{name}': welcome,
    r'/': home,
    r'/login': parse_form
})

app = App(router)
app.start_server()
