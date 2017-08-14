# Web View
from functools import wraps
from server.core.models.delayed_tasks import DelayedTaskManager
from server.core.models.jenkins_groups import JenkinsGroupManager
from server.core.models.jenkins_jobs import JenkinsJobManager
from server.core.clients.gitlab_client import GitLabClient


def set_log_marker(func):
    """
        Decorator for set marker in view
    """

    @wraps(func)
    async def wrapper(*args):
        self = args[0]
        self._marker = self.request.marker
        return await func(*args)

    return wrapper


def create_delayed_manager(func):
    """
        Decorator for create delayed_manager object
    """

    @wraps(func)
    async def wrapper(*args):
        self = args[0]
        db = self.request.app['db_pool']
        db_tables = self.request.app['sa_tables']
        self.delayed_task_manager = DelayedTaskManager(self.request.marker, db, db_tables)
        return await func(*args)

    return wrapper


def create_jenkins_group_manager(func):
    """
        Decorator for create jenkins_group_manager object
    """

    @wraps(func)
    async def wrapper(*args):
        self = args[0]
        db = self.request.app['db_pool']
        db_tables = self.request.app['sa_tables']
        self.jenkins_group_manager = JenkinsGroupManager(self.request.marker, db, db_tables)
        return await func(*args)

    return wrapper


def create_jenkins_job_manager(func):
    """
        Decorator for create jenkins_job_manager object
    """

    @wraps(func)
    async def wrapper(*args):
        self = args[0]
        db = self.request.app['db_pool']
        db_tables = self.request.app['sa_tables']
        self.jenkins_job_manager = JenkinsJobManager(self.request.marker, db, db_tables)
        return await func(*args)

    return wrapper


def create_gitlab_client(func):
    """
        Decorator for create gitlab_client object
    """

    @wraps(func)
    async def wrapper(*args):
        self = args[0]
        db = self.request.app['db_pool']
        db_tables = self.request.app['sa_tables']
        gitlab_config = self.request.app['config']['gitlab']
        self.gitlab_client = GitLabClient(self.request.marker,
                                          gitlab_config['url'],
                                          gitlab_config['access_token'])
        return await func(*args)

    return wrapper
