import enum
import hashlib
import json
from sqlalchemy import desc

from server.core.common import LoggingMixin
from server.core.models import RecordNotFound


class JenkinsGroup(object):
    """Data class for JenkinsGroup"""

    def __init__(self):
        self.id = None
        self.name = None
        self.jobs_base_path = None

    @property
    def values(self):
        result = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        return result

    @staticmethod
    def make(name, jobs_base_path):
        obj = JenkinsGroup()
        obj.name = name
        obj.jobs_base_path = jobs_base_path
        return obj

    def __repr__(self):
        msg = "JenkinsGroup %s" % (self.values)
        return msg

class JenkinsGroupManager(LoggingMixin):
    """ Class for managment data in jenkins_groups table"""

    def __init__(self, marker, db_pool, tables):
        self._marker = marker
        self.db_pool = db_pool
        self._jenkins_groups = tables['jenkins_groups']

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

        colums = self._jenkins_groups.c
        async with self.db_pool.acquire() as conn:
            q = self._jenkins_groups.select()

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

    async def find_by_name(name):
        """
        Get one JenkinsGroup object by name

        Args:
            name - group name

        Return:
            JenkinsGroup object

        Exceptions:
                RecordNotFound
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            q = self._jenkins_groups.select().where(self._jenkins_groups.c.name == name)
            self._logging_debug(q)
            result = await conn.execute(q)
            row = await result.fetchone()
            if row is None:
                msg = "JenkinsGroup with name: {} does not exists"
                raise RecordNotFound(msg.format(name))
            obj = await self._mapping_row_to_obj(row)
            self._logging_debug(obj)
            return obj

    async def get(self, grop_id):
        """
        Get one JenkinsGroup object by id field

        Args:
            grop_id - value id field

        Return:
            JenkinsGroup object

        Exceptions:
                RecordNotFound
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            q = self._jenkins_groups.select().where(self._jenkins_groups.c.id == grop_id)
            self._logging_debug(q)
            result = await conn.execute(q)
            row = await result.fetchone()
            if row is None:
                msg = "JenkinsGroup with id: {} does not exists"
                raise RecordNotFound(msg.format(grop_id))
            obj = await self._mapping_row_to_obj(row)
            self._logging_debug(obj)
            return obj

    async def create(self, jenkins_group):
        """
        Create JenkinsGroup object

        Args:
            jenkins_group - JenkinsGroup object

        Return:
            JenkinsGroup object

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            self._logging_debug(jenkins_group.values)
            trans = await conn.begin()
            try:
                q = self._jenkins_groups.insert(). \
                    values(jenkins_group.values)
                result = await conn.execute(q)
                await trans.commit()
                self._logging_debug('Commit')
                return await self.get(result.lastrowid)
            except Exception as e:
                self._logging_debug('Rollback')
                await trans.rollback()
                raise

    async def update(self, jenkins_group):
        """
        Update values

        Args:
            jenkins_group - JenkinsGroup

        Return:
            None

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            trans = await conn.begin()
            try:
                q = self._jenkins_groups. \
                    update(self._jenkins_groups.c.id == jenkins_group.id). \
                    values(jenkins_group.values)
                self._logging_debug(q)
                await conn.execute(q)
                await trans.commit()
            except Exception as e:
                self._logging_debug('Rollback')
                await trans.rollback()
                raise

    async def delete(self, grop_id):
        """
        Delete row

        Args:
            grop_id - JenkinsGroup id

        Return:
            None

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            trans = await conn.begin()
            try:
                q = self._jenkins_groups.delete(self._jenkins_groups.c.id == grop_id)
                self._logging_debug(q)
                await conn.execute(q)
                await trans.commit()
            except Exception as e:
                self._logging_debug('Rollback')
                await trans.rollback()
                raise

    # private methods
    def _columns(self):
        return self._jenkins_groups.c.keys()

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
