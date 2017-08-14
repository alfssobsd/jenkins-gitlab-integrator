from aiohttp import web

from server.core.clients.gitlab_client import GitLabWebHook, GitLabProjectNotFound

class WebHookApiMixin(object):
    """
        Methods for manage webhook in gitlab
    """

    async def _create_job_webhook(self, group, job):
        # generate webhook url
        hook_url = self._gen_hook_url(group, job)
        new_hook = GitLabWebHook()
        new_hook.url = hook_url
        new_hook.token = self.request.app['config']['gitlab_webhook_token']
        # create new gitlab hook
        await self.gitlab_client.create_webhook(job.gitlab_project_id, new_hook)

    async def _delete_job_webhook(self, group, job, ignore_errors=False):
        # generate webhook url
        hook_url = self._gen_hook_url(group, job)
        # delete hooks
        try:
            hooks = await self.gitlab_client.get_webhooks(job.gitlab_project_id)
            for hook in hooks:
                if hook.url is not None and hook.url == hook_url:
                    await self.gitlab_client.delete_webhook(job.gitlab_project_id, hook.id)
        except GitLabProjectNotFound as e:
            if not ignore_errors:
                raise

    def _gen_hook_url(self, group, job):
        return "%s/gitlab/group/%s/job/%s" % (self.request.app['config']['server_url'], group.name, job.name)
