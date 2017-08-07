from aiohttp import web
from server.core.common import LoggingMixin

class IndexView(web.View, LoggingMixin):
    """
        Redirect to UI
    """
    async def get(self):
        ui_url = self.request.app.router['index_ui_root'].url()
        response = web.HTTPFound(ui_url)
        return response

class IndexUIView(web.View, LoggingMixin):
    """
        index.html
    """
    async def get(self):
        return web.FileResponse(str( self.request.app['PROJECT_ROOT']  / 'static' / 'index.html') )

