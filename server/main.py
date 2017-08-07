import argparse
import pathlib
import logging
import sys
import base64
import asyncio
import pymysql
import sqlalchemy as sa
from aiohttp import web
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy
from aiomysql.sa import create_engine
from trafaret_config import commandline

import server.middlewares as middlewares
from server.utils import TRAFARET
from .core.views.debug import DebugView
from .core.views.gitlab import GitLabWebhookView
from .core.views.common import LoginApiV1View, IndexUIView, IndexView, StatsView
from .core.views.admin_api import AdminApiV1ConfigView, AdminApiV1DelayedTasksView,\
 AdminApiV1DelayedTaskDetailView, AdminApiV1DelayedTaskChangeStatusView, AdminApiV1JenkinsGroupView, \
 AdminApiV1JenkinsGroupSearchView
from .core.workers.gitlab_worker import GitLabWorker
from .core.security.policy import FileAuthorizationPolicy

class SecurityMixnin(object):
    def setup_security(self):
        secret_key = base64.urlsafe_b64decode(self.app['config']['session_secret'])
        setup_session(self.app, EncryptedCookieStorage(secret_key))
        setup_security(self.app, SessionIdentityPolicy(), FileAuthorizationPolicy(self.app['config']['users']))

class RoutesMixin(object):

    PROJECT_ROOT = pathlib.Path(__file__).parent

    def setup_routes(self):
        self.app['PROJECT_ROOT'] = self.PROJECT_ROOT
        self.app.router.add_get('/', IndexView, name='index')
        self.app.router.add_get('/ui/', IndexUIView, name='index_ui_root')
        self.app.router.add_get('/ui/{path:.*}', IndexUIView, name='index_ui')
        self.app.router.add_get('/api/v1/stats', StatsView, name='api_v1_stats')
        self.app.router.add_static('/static/', path=str(self.PROJECT_ROOT / 'static'), name='static')
        self.app.router.add_post('/api/v1/login', LoginApiV1View, name='api_v1_login')
        self.app.router.add_delete('/api/v1/logout', LoginApiV1View, name='api_v1_logout')
        #Config
        self.app.router.add_get('/admin/api/v1/config', AdminApiV1ConfigView, name='admin_api_v1_config')
        #DelayedTask
        self.app.router.add_get('/admin/api/v1/delayed-task', AdminApiV1DelayedTasksView, name='admin_api_v1_delayed_task')
        self.app.router.add_get('/admin/api/v1/delayed-task/{id}', AdminApiV1DelayedTaskDetailView, name='admin_api_v1_delayed_task_view')
        self.app.router.add_post('/admin/api/v1/delayed-task/{id}/status', AdminApiV1DelayedTaskChangeStatusView, name='admin_api_v1_delayed_task_status_view')
        #JenkinsGroup search
        self.app.router.add_get('/admin/api/v1/jenkins-group', AdminApiV1JenkinsGroupSearchView, name='admin_api_v1_jenkins_group_search')
        #JenkinsGroup managment
        self.app.router.add_post('/admin/api/v1/jenkins-group', AdminApiV1JenkinsGroupView, name='admin_api_v1_jenkins_group_create')
        self.app.router.add_get('/admin/api/v1/jenkins-group/{id}', AdminApiV1JenkinsGroupView, name='admin_api_v1_jenkins_group_show')
        self.app.router.add_put('/admin/api/v1/jenkins-group/{id}', AdminApiV1JenkinsGroupView, name='admin_api_v1_jenkins_group_update')
        self.app.router.add_delete('/admin/api/v1/jenkins-group/{id}', AdminApiV1JenkinsGroupView, name='admin_api_v1_jenkins_group_delete')
        #
        self.app.router.add_post('/debug/post/webhook', DebugView)
        self.app.router.add_get('/debug/get/webhook', DebugView)
        self.app.router.add_post('/gitlab/group/{group}/job/{job_name}', GitLabWebhookView)


class CommandLineOptionsMixin(object):
    def read_cmdline(self, argv):
        ap = argparse.ArgumentParser()
        commandline.standard_argparse_options(ap, default_config='./config/server.yml')
        return ap.parse_args(argv)

class ConfigMixin(object):
    def read_config(self, options):
        self.app['config'] = commandline.config_from_options(options, TRAFARET)


class BackgroundWorkerMixin(object):
    async def init_backgroud_worker(self, app):
        app['background_worker'] = app.loop.create_task(self._create_background_worker(app))

    async def cleanup_backgroud_worker(self, app):
        app['background_worker'].cancel()
        await app['background_worker']

    async def _create_background_worker(self, app):
        gitlab_worker = GitLabWorker(app)
        try:
            await gitlab_worker.run()
        except asyncio.CancelledError:
            pass
        finally:
            await gitlab_worker.stop()


class DBConnectorMixin(object):

    async def init_connect_db(self, app):
        app['config']['mysql']['autocommit'] = True
        engine = await create_engine(loop=app.loop, **app['config']['mysql'])
        app['db_pool'] = engine

    async def close_connect_db(self, app):
        app['db_pool'].close()
        await app['db_pool'].wait_closed()

class DBTablesMixin(object):
    def _get_mysql_creator(self):
        db_settings = {
            'host': self.app['config']['mysql']['host'],
            'db': self.app['config']['mysql']['db'],
            'user': self.app['config']['mysql']['user'],
            'password': self.app['config']['mysql']['password'],
            'port': self.app['config']['mysql']['port'],
            'autocommit': True,
        }

        return pymysql.connect(**db_settings)

    def _get_mysql_metadata(self, conn):
        meta = sa.MetaData(conn)
        meta.reflect()
        return meta

    def init_sa_tables(self):
        conn = sa.create_engine('mysql+pymysql://', creator=self._get_mysql_creator)
        self.app['sa_metadata'] = self._get_mysql_metadata(conn)
        self.app['sa_tables'] = self.app['sa_metadata'].tables


class LoggerSetupMixin(object):
    def setup_root_logger(self):
        level = logging.getLevelName(self.app['config']['log_level'])
        logging.basicConfig(level=level, format='%(asctime)s:%(levelname)s:%(message)s')


class Server(RoutesMixin, CommandLineOptionsMixin, ConfigMixin, DBConnectorMixin,
    DBTablesMixin, LoggerSetupMixin, BackgroundWorkerMixin, SecurityMixnin):
    """
    Server entrypoint
    """
    SERVER_VERSION = "1.0.3"

    def __init__(self, argv):
        self.app = web.Application(loop=asyncio.get_event_loop())
        self.read_config(self.read_cmdline(argv))
        self.setup_root_logger()
        self.setup_security()
        self.setup_routes()
        self.init_sa_tables()
        self.app['app_version'] = self.SERVER_VERSION

        self.app.middlewares.append(middlewares.uuid_marker_request)
        self.app.on_startup.append(self.init_connect_db)
        self.app.on_cleanup.append(self.close_connect_db)

        if self.app['config']['workers']['enable']:
            self.app.on_startup.append(self.init_backgroud_worker)
            self.app.on_cleanup.append(self.cleanup_backgroud_worker)

        web.run_app(self.app, host=self.app['config']['host'], port=self.app['config']['port'])


if __name__ == '__main__':
    server = Server(sys.argv[1:])
