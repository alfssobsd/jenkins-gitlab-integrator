import uuid
import logging

from aiohttp import web


async def uuid_marker_request(app, handler):
    """
    Add to all request unique id
    """

    async def middleware(request):
        request.marker = "web-" + uuid.uuid4().hex
        response = await handler(request)
        return response

    return middleware


async def handle_error(message, status):
    return web.json_response({'error': str(message), 'status': status}, status=status)

async def handle_500(message):
    return web.json_response({'error': str(message), 'status': 500}, status=500)

async def error_middleware(app, handler):
    async def middleware_handler(request):
        try:
            response = await handler(request)
            return response
        except web.HTTPException as ex:
            logging.exception(ex)
            return await handle_error(ex.reason, ex.status)
        except Exception as ex:
            logging.exception(ex)
            return await handle_500(ex)

    return middleware_handler
