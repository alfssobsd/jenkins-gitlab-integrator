import enum
import hashlib

from sqlalchemy import desc

from server.core.common import LoggingMixin
from server.core.models import RecordNotFound


class DelayedTaskStatus(enum.Enum):
    NEW = 1
    SUCCESS = 2
    CANCELED = 3


class DelayedTaskType(enum.Enum):
    GITLAB_MERGE_REQ = 1
    GITLAB_PUSH = 2


class DelayedTask(object):
    """Data class for DelayedTask"""

    def __init__(self):
        self.id = None
        self.sha1 = None
        self._task_status = DelayedTaskStatus.NEW
        self._task_type = DelayedTaskType.GITLAB_PUSH
        self.group = None
        self.job_name = None
        self.branch = None
        self.counter_attempts = 0
        self.gitlab_merge_comment_id = None

    @property
    def task_status(self):
        return self._task_status.name

    @task_status.setter
    def task_status(self, value):
        if type(value) == DelayedTaskStatus:
            self._task_status = value
        else:
            self._task_status = DelayedTaskStatus[value]

    @property
    def task_type(self):
        return self._task_type.name

    @task_type.setter
    def task_type(self, value):
        if type(value) == DelayedTaskType:
            self._task_type = value
        else:
            self._task_type = DelayedTaskType[value]

    @property
    def uniq_md5sum(self):
        md5 = hashlib.md5()
        md5.update(self.task_type.encode('utf-8'))
        md5.update(self.group.encode('utf-8'))
        md5.update(self.job_name.encode('utf-8'))
        md5.update(self.sha1.encode('utf-8'))
        md5.update(self.branch.encode('utf-8'))

        return md5.hexdigest()

    @uniq_md5sum.setter
    def uniq_md5sum(self, value):
        pass

    @property
    def values(self):
        result = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        result['uniq_md5sum'] = self.uniq_md5sum
        result['task_type'] = self.task_type
        result['task_status'] = self.task_status
        return result

    def __repr__(self):
        msg = "DelayedTask %s" % self.values
        return msg

    @staticmethod
    def make_push_task(group, job_name, sha1, branch):
        return DelayedTask.make_task(DelayedTaskType.GITLAB_PUSH, group, job_name, sha1, branch)

    @staticmethod
    def make_merge_task(group, job_name, sha1, branch, project_id, merge_id):
        task = DelayedTask.make_task(DelayedTaskType.GITLAB_MERGE_REQ, group, job_name, sha1, branch)
        task.gitlab_project_id = project_id
        task.gitlab_merge_id = merge_id
        return task

    @staticmethod
    def make_task(task_type, group, job_name, sha1, branch):
        obj = DelayedTask()
        obj.task_type = task_type
        obj.group = group
        obj.job_name = job_name
        obj.sha1 = sha1
        obj.branch = branch
        obj.counter_attempts = 0
        return obj


class DelayedTaskManager(LoggingMixin):
    """ Class for managment data in delayed_tasks table"""

    def __init__(self, marker, db_pool, tables):
        self._marker = marker
        self.db_pool = db_pool
        self._delayed_tasks = tables['delayed_tasks']

    async def search(self, task_type=None, task_status=None, group=None,
                     job_name=None, branch=None, sha1=None, limit=150):
        """
            Search delayed_tasks by fields

        Args:
            task_type - task type
            task_status - task status
            group  - group name
            job_name - job_name
            branch - branch
            sha1  - sha1
        Return:
            list[DelayedTask obj, DelayedTask obj]

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        self._logging_debug("Search: %s %s %s %s %s %s" % (task_type,
                                                           task_status, group, job_name, branch, sha1))

        colums = self._delayed_tasks.c
        async with self.db_pool.acquire() as conn:
            q = self._delayed_tasks.select()

            if task_type:
                q = q.where(colums.task_type == task_type)

            if task_status:
                q = q.where(colums.task_status == task_status)

            if group:
                q = q.where(colums.group == group)

            if job_name:
                q = q.where(colums.job_name == job_name)

            if branch:
                q = q.where(colums.branch == branch)

            if sha1:
                q = q.where(colums.sha1 == sha1)

            if limit:
                q = q.limit(limit)

            q = q.order_by(desc(colums.id))

            self._logging_debug(q)
            result = await conn.execute(q)
            rows = await result.fetchall()
            list_data_obj = await self._mapping_from_tuple(rows)
            return list_data_obj

    async def get_or_create(self, delayed_task):
        """
        Create or get exist DelayedTask object

        Args:
            delayed_task - DelayedTask object

        Return:
            DelayedTask object

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            self._logging_debug(delayed_task.values)
            trans = await conn.begin()
            try:
                q = self._delayed_tasks.insert(). \
                    values(delayed_task.values)
                await conn.execute(q)
                await trans.commit()
                self._logging_debug('Commit')
            except Exception as e:
                self._logging_debug('Rollback')
                self._logging_debug(e)
                await trans.rollback()

            fetch_task_obj = await self.get_by_uniq_md5sum(delayed_task.uniq_md5sum)
            return fetch_task_obj

    async def get_by_uniq_md5sum(self, uniq_md5sum):
        """
        Get one DelayedTask object by uniq_md5sum field

        Args:
            uniq_md5sum - value uniq_md5sum field

        Return:
            DelayedTask object

        Exceptions:
                RecordNotFound
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            q = self._delayed_tasks.select().where(self._delayed_tasks.c.uniq_md5sum == uniq_md5sum)
            self._logging_debug(q)
            result = await conn.execute(q)
            row = await result.fetchone()
            if row is None:
                msg = "DelayedTask with uniq_md5sum: {} does not exists"
                raise RecordNotFound(msg.format(uniq_md5sum))
            obj = await self._mapping_row_to_delayed_task(row)
            self._logging_debug(obj)
            return obj

    async def get(self, task_id):
        """
        Get one DelayedTask object by id field

        Args:
            id - value id field

        Return:
            DelayedTask object

        Exceptions:
                RecordNotFound
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            q = self._delayed_tasks.select().where(self._delayed_tasks.c.id == task_id)
            self._logging_debug(q)
            result = await conn.execute(q)
            row = await result.fetchone()
            if row is None:
                msg = "DelayedTask with id: {} does not exists"
                raise RecordNotFound(msg.format(task_id))
            obj = await self._mapping_row_to_delayed_task(row)
            self._logging_debug(obj)
            return obj

    async def get_by_status(self, task_status, limit=150):
        """
        Get list DelayedTask by task_status

        Args:
            task_status - DelayedTaskStatus
            limit - limit rows
        Return:
            list[DelayedTask obj, DelayedTask obj]

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        self._logging_debug("Get delayed_task with status: %s" % task_status.name)
        return await self.search(task_status=task_status.name, limit=limit)

    async def get_by_status_new(self, limit=150):
        """
            Get list DelayedTask by task_status = NEW
            Args:
                limit - limit rows
            Return:
                list[DelayedTask obj, DelayedTask obj]
        """
        list_data_obj = await self.get_by_status(DelayedTaskStatus.NEW, limit)
        return list_data_obj

    async def clear_attempts(self, delayed_task_id):
        """
            Clear attempts -> set attempts = 0

            Args:
                delayed_task_id - DelayedTask id

            Return:
                None
            Exceptions:
                RecordNotFound
                pymysql.err
                and anower from sqlalchemy
        """
        self._logging_debug("Clear delayed_task attempts with id: %d" % delayed_task_id)
        async with self.db_pool.acquire() as conn:
            trans = await conn.begin()
            try:
                q = self._delayed_tasks.update(self._delayed_tasks.c.id == delayed_task_id).values(counter_attempts=0)
                await conn.execute(q)
                await trans.commit()
            except Exception:
                self._logging_debug('Rollback')
                await trans.rollback()
                raise

    async def increment_attempts(self, delayed_task_id):
        """
        Increment counter attempt

        Args:
            delayed_task_id - DelayedTask id

        Return:
            None

        Exceptions:
                RecordNotFound
                pymysql.err
                and anower from sqlalchemy
        """
        self._logging_debug("Increment delayed_task attempts with id: %d" % delayed_task_id)
        async with self.db_pool.acquire() as conn:
            trans = await conn.begin()
            try:
                q = self._delayed_tasks.update(self._delayed_tasks.c.id == delayed_task_id).values(
                    counter_attempts=self._delayed_tasks.c.counter_attempts + 1)
                await conn.execute(q)
                await trans.commit()
            except Exception:
                self._logging_debug('Rollback')
                await trans.rollback()
                raise

    async def update_values(self, delayed_task_id, values):
        """
        Update values

        Args:
            delayed_task_id - DelayedTask id
            values - hash {"field": "value"}

        Return:
            None

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            trans = await conn.begin()
            try:
                q = self._delayed_tasks.update(self._delayed_tasks.c.id == delayed_task_id).values(values)
                self._logging_debug(q)
                await conn.execute(q)
                await trans.commit()
            except Exception:
                self._logging_debug('Rollback')
                await trans.rollback()
                raise

    async def set_gitlab_merge_comment_id(self, delayed_task_id, gitlab_merge_comment_id):
        self._logging_debug("Set gitlab_merge_comment_id %d for delayed task with id: %d"
                            % (gitlab_merge_comment_id, delayed_task_id))
        await self.update_values(delayed_task_id, {'gitlab_merge_comment_id': gitlab_merge_comment_id})

    async def set_status(self, delayed_task_id, task_status):
        """
        Set task_status

        Args:
            delayed_task_id - DelayedTask id
            task_status - DelayedTaskStatus

        Return:
            None

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        self._logging_debug("Set status %s for delayed_task with id: %d" % (task_status.name, delayed_task_id))
        await self.update_values(delayed_task_id, {'task_status': task_status.name})

    async def set_status_new(self, delayed_task_id):
        """
        Set task_status to NEW

        Args:
            delayed_task_id - DelayedTask id

        Return:
            None

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        await self.set_status(delayed_task_id, DelayedTaskStatus.NEW)

    async def set_status_success(self, delayed_task_id):
        """
        Set task_status to SUCCESS

        Args:
            delayed_task_id - DelayedTask id

        Return:
            None

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        await self.set_status(delayed_task_id, DelayedTaskStatus.SUCCESS)

    async def set_status_canceled(self, delayed_task_id):
        """
        Set task_status to CANCELED

        Args:
            delayed_task_id - DelayedTask id

        Return:
            None

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        await self.set_status(delayed_task_id, DelayedTaskStatus.CANCELED)

    async def delete(self, delayed_task_id):
        """
        Delete row

        Args:
            delayed_task_id - DelayedTask id

        Return:
            None

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            trans = await conn.begin()
            try:
                q = self._delayed_tasks.delete(self._delayed_tasks.c.id == delayed_task_id)
                self._logging_debug(q)
                await conn.execute(q)
                await trans.commit()
            except Exception:
                self._logging_debug('Rollback')
                await trans.rollback()
                raise

    # private methods
    def _columns(self):
        return self._delayed_tasks.c.keys()

    async def _mapping_row_to_delayed_task(self, row):
        """
        Mapping row to DelayedTask object

        Return:
            DelayedTask object
        """
        data_obj = DelayedTask()
        for column in self._columns():
            data_obj.__setattr__(column, row[column])

        return data_obj

    async def _mapping_from_tuple(self, rows):
        """
        Mapping tuple(row,row) to list [DelayedTask obj, DelayedTask obj]

        Return:
            list[DelayedTask obj]
        """
        result = []
        for row in rows:
            result.append(await self._mapping_row_to_delayed_task(row))
        return result
