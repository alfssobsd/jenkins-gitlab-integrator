#Web View
from functools import wraps
from server.core.models.delayed_tasks import DelayedTaskManager

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
