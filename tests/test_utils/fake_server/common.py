import asyncio
import socket
import json
from functools import wraps
from aiohttp import web
from aiohttp.test_utils import unused_port


def http_method(method, path):
    def wrapper(func):
        func.__method__ = method
        func.__path__ = path
        return func

    return wrapper


def head(path):
    return http_method('HEAD', path)


def get(path):
    return http_method('GET', path)


def delete(path):
    return http_method('DELETE', path)


def options(path):
    return http_method('OPTIONS', path)


def patch(path):
    return http_method('PATCH', path)


def post(path):
    return http_method('POST', path)


def put(path):
    return http_method('PUT', path)


def trace(path):
    return http_method('TRACE', path)


def auth_gilab_token_required(func):
    @wraps(func)
    async def wrapper(*args):
        if args[-1].headers['Private-Token'] != 'test_token':
            raise web.HTTPForbidden()

        return await func(*args)

    return wrapper


def auth_basic_required(func):
    @wraps(func)
    async def wrapper(*args):
        # user = username, password = password --> dXNlcm5hbWU6cGFzc3dvcmQ=
        if args[-1].headers['Authorization'] != 'Basic dXNlcm5hbWU6cGFzc3dvcmQ=':
            raise web.HTTPForbidden()

        return await func(*args)

    return wrapper


class FakeHTTPServer:
    def __init__(self, *, loop):
        self.loop = loop
        self.app = web.Application(loop=loop)
        for name in dir(self.__class__):
            func = getattr(self.__class__, name)
            if hasattr(func, '__method__'):
                self.app.router.add_route(func.__method__,
                                          func.__path__,
                                          getattr(self, name))
        self.handler = None
        self.server = None

        self._server_addr = '127.0.0.1'
        self._server_port = 40000

    def load_fixture(self, path):
        data = None
        with open(path) as data_file:
            data = json.load(data_file)
        return data

    async def start(self):
        port = unused_port()
        self.handler = self.app.make_handler(loop=self.loop)
        self.server = await self.loop.create_server(self.handler,
                                                    self._server_addr, port)
        self._server_port = port
        return self._server_addr, self._server_port

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()
        await self.app.shutdown()
        await self.handler.shutdown()
        await self.app.cleanup()

# class FakeResolver:
#     _LOCAL_HOST = {0: '127.0.0.1',
#                    socket.AF_INET: '127.0.0.1',
#                    socket.AF_INET6: '::1'}

#     def __init__(self, fakes, *, loop):
#         """fakes -- dns -> port dict"""
#         self._fakes = fakes
#         self._resolver = DefaultResolver(loop=loop)

#     async def resolve(self, host, port=0, family=socket.AF_INET):
#         fake_port = self._fakes.get(host)
#         if fake_port is not None:
#             return [{'hostname': host,
#                      'host': self._LOCAL_HOST[family], 'port': fake_port,
#                      'family': family, 'proto': 0,
#                      'flags': socket.AI_NUMERICHOST}]
#         else:
#             return await self._resolver.resolve(host, port, family)
