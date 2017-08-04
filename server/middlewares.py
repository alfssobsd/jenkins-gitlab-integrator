import uuid

async def uuid_marker_request(app, handler):
    """
    Add to all request unique id
    """
    async def middleware(request):
        request.marker = "web-" + uuid.uuid4().hex
        response = await handler(request)
        return response
    return middleware
