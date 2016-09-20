# Simple Python Framework from Scratch

> Features:
>* Must handle GET and POST HTTP requests. You can get a brief overview of HTTP in this wiki article).
>* Must be asynchronous (I'm loving the Python 3 asyncio module).
>* Must include simple routing logic along with capturing parameters.
>* Must provide a simple user-facing API like other cool microframeworks.
>* Must handle authentication, because it's cool to learn that too (saved for Part 2).

> Constraints:
>* Will only handle a small subset of HTTP/1.1: no transfer-encoding, no http-auth, no content-encoding (gzip), no persistant connections.
>* No MIME-guessing for responses - users will have to set this manually.
>* No WSGI - just simple TCP connection handling.
>* No database support.

# Reference

* [Simple Python Framework from Scratch](http://mattscodecave.com/posts/simple-python-framework-from-scratch.html)