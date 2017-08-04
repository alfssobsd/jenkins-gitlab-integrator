import enum
import hashlib
import json
from sqlalchemy import desc

from server.core.common import LoggingMixin

class JenkinsGroup(object):
    """Data class for JenkinsGroup"""
    def __init__(self):
        self.id = None
        self.name = None
        self.jobs_base_path = None

    @property
    def values(self):
        result = {k: v for k, v in self.__dict__ .items() if not k.startswith('_')}
        return result

    @staticmethod
    def make(name, jobs_base_path):
        obj = JenkinsGroup()
        obj.name = name
        obj.jobs_base_path = jobs_base_path
        return obj

class JenkinsGroupManager(LoggingMixin):
    """ Class for managment data in jenkins_groups table"""

    def __init__(self, marker, db_pool, tables):
        self._marker = marker
        self.db_pool = db_pool
        self._jenkins_job_groups = tables['jenkins_groups']

    async def search(self, name, limit=150):
        """
        Search jenkins_groups by fields

        Args:
            name - group name
        Return:
            list[JenkinsGroup obj, JenkinsGroup obj]

        Exceptions:
                pymysql.err
        """
        self._logging_debug("Search: %s" % (name))

        colums = self._jenkins_job_groups.c
        async with self.db_pool.acquire() as conn:
            q = self._jenkins_job_groups.select()

            if name:
                q = q.where(colums.name.startswith(name))

            if limit:
                q = q.limit(limit)

            q = q.order_by(desc(colums.name))

            self._logging_debug(q)
            result = await conn.execute(q)
            rows = await result.fetchall()
            list_data_obj = await self._mapping_from_tuple(rows)
            return list_data_obj

    async def get(self, id):
        pass

    async def create(self, jenkins_group):
        pass

    async def update(self, jenkins_group):
        pass

    async def delete(self, jenkins_group):
        pass

    #private methods
    def _columns(self):
        return self._jenkins_job_groups.c.keys()

    async def _mapping_row_to_obj(self, row):
        """
        Mapping row to JenkinsGroup object

        Return:
            JenkinsGroup object
        """
        data_obj = JenkinsGroup()
        for column in self._columns():
            data_obj.__setattr__(column, row[column])

        return data_obj

    async def _mapping_from_tuple(self, rows):
        """
        Mapping tuple(row,row) to list [JenkinsGroup obj, JenkinsGroup obj]

        Return:
            list[JenkinsGroup obj]
        """
        result = []
        for row in rows:
            result.append(await self._mapping_row_to_obj(row))
        return result
