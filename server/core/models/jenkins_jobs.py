from sqlalchemy import desc

from server.core.common import LoggingMixin
from server.core.models import RecordNotFound


class JenkinsJob(object):
    """Data class for JenkinsJob"""

    def __init__(self):
        self.id = None
        self.name = None
        self.jenkins_group_id = None
        self.jenkins_job_perent_id = None
        self.gitlab_project_id = None

    @property
    def values(self):
        result = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        return result

    @staticmethod
    def make(name, jenkins_group_id, jenkins_job_perent_id, gitlab_project_id):
        obj = JenkinsJob()
        obj.name = name
        obj.jobs_base_path = jenkins_group_id
        obj.jenkins_job_perent_id = jenkins_job_perent_id
        obj.gitlab_project_id = gitlab_project_id

        return obj

    def __repr__(self):
        msg = "JenkinsJob %s" % (self.values)
        return msg

class JenkinsJobPathFinder(object):
    """" Class for search jobs path """

    def __init__(self, jobs):
        self.jobs = jobs

    def get_all_paths(self):
        graph = self._prepare_graph(self.jobs)
        paths = list()
        for job in graph[None]:
            paths += list(self._paths(graph, job))
        return paths

    def _prepare_graph(self, jobs):
        """ Convert job list to graph """

        graph = dict()
        for job in jobs:
            if not job.id in graph:
                graph[job.id] = list()
            if not job.jenkins_job_perent_id in graph:
                graph[job.jenkins_job_perent_id] = list()
            graph[job.jenkins_job_perent_id].append(job)
        return graph

    def _paths(self, graph, job):
        """ Generate the maximal cycle-free paths in graph starting at job """

        path = [job]
        seen = {job.id}
        def search():
            dead_end = True
            for neighbour_job in graph[path[-1].id]:
                if neighbour_job.id not in seen:
                    dead_end = False
                    seen.add(neighbour_job.id)
                    path.append(neighbour_job)
                    yield from search()
                    path.pop()
                    seen.remove(neighbour_job.id)
            if dead_end:
                yield list(path)
        yield from search()

class JenkinsJobManager(LoggingMixin):
    """ Class for managment data in jenkins_jobs table"""

    def __init__(self, marker, db_pool, tables):
        self._marker = marker
        self.db_pool = db_pool
        self._jenkins_jobs = tables['jenkins_jobs']

    async def find_by_groud_id(self, group_id):
        """
        Search jenkins_groups by group_id

        Args:
            group_id - group id
        Return:
            list[JenkinsGroup obj, JenkinsGroup obj]

        Exceptions:
                pymysql.err
        """
        self._logging_debug("Find by group id: %d" % group_id)

        columns = self._jenkins_jobs.c
        async with self.db_pool.acquire() as conn:
            q = self._jenkins_jobs.select().\
                where(columns.jenkins_group_id == group_id).\
                order_by(columns.id)

            self._logging_debug(q)

            result = await conn.execute(q)
            rows = await result.fetchall()
            list_data_obj = await self._mapping_from_tuple(rows)
            return list_data_obj

    async def get(self, job_id):
        """
        Get one JenkinsJob object by id field

        Args:
            job_id - value id field

        Return:
            JenkinsJob object

        Exceptions:
                RecordNotFound
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            q = self._jenkins_jobs.select().where(self._jenkins_jobs.c.id == job_id)
            self._logging_debug(q)
            result = await conn.execute(q)
            row = await result.fetchone()
            if row is None:
                msg = "JenkinsGroup with id: {} does not exists"
                raise RecordNotFound(msg.format(job_id))
            obj = await self._mapping_row_to_obj(row)
            self._logging_debug(obj)
            return obj

    async def create(self, jenkins_job):
        """
        Create JenkinsGroup object

        Args:
            jenkins_job - JenkinsJob object

        Return:
            JenkinsJob object

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            self._logging_debug(jenkins_job.values)
            trans = await conn.begin()
            try:
                q = self._jenkins_jobs.insert(). \
                    values(jenkins_job.values)
                result = await conn.execute(q)
                await trans.commit()
                self._logging_debug('Commit')
                return await self.get(result.lastrowid)
            except Exception as e:
                self._logging_debug('Rollback')
                await trans.rollback()
                raise

    async def update(self, jenkins_job):
        """
        Update values

        Args:
            jenkins_group - JenkinsJob

        Return:
            None

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            trans = await conn.begin()
            try:
                q = self._jenkins_jobs. \
                    update(self._jenkins_jobs.c.id == jenkins_job.id). \
                    values(jenkins_job.values)
                self._logging_debug(q)
                result = await conn.execute(q)
                await trans.commit()
                self._logging_debug('Commit')
                return await self.get(jenkins_job.id)
            except Exception as e:
                self._logging_debug('Rollback')
                await trans.rollback()
                raise

    async def delete(self, job_id):
        """
        Delete row

        Args:
            job_id - JenkinsJob id

        Return:
            None

        Exceptions:
                pymysql.err
                and anower from sqlalchemy
        """
        async with self.db_pool.acquire() as conn:
            trans = await conn.begin()
            try:
                q = self._jenkins_jobs.delete(self._jenkins_jobs.c.id == job_id)
                self._logging_debug(q)
                await conn.execute(q)
                await trans.commit()
            except Exception as e:
                self._logging_debug('Rollback')
                await trans.rollback()
                raise

    # private methods
    def _columns(self):
        return self._jenkins_jobs.c.keys()

    async def _mapping_row_to_obj(self, row):
        """
        Mapping row to JenkinsJob object

        Return:
            JenkinsGroup object
        """
        data_obj = JenkinsJob()
        for column in self._columns():
            data_obj.__setattr__(column, row[column])

        return data_obj

    async def _mapping_from_tuple(self, rows):
        """
        Mapping tuple(row,row) to list [JenkinsJob obj, JenkinsJob obj]

        Return:
            list[JenkinsJob obj]
        """
        result = []
        for row in rows:
            result.append(await self._mapping_row_to_obj(row))
        return result
