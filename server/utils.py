import trafaret as T

"""
trafaret for server config
"""
TRAFARET = T.Dict({
    T.Key('session_secret'): T.String(),
    T.Key('users'): T.Any(),
    T.Key('mysql'):
        T.Dict({
            'db': T.String(),
            'host': T.String(),
            'user': T.String(),
            'password': T.String(allow_blank=True),
            'port': T.Int(),
            'minsize': T.Int(),
            'maxsize': T.Int(),
            }),
    T.Key('gitlab'):
        T.Dict({
            'url': T.String(),
            'access_token': T.String(),
            }),
    T.Key('workers'):
        T.Dict({
            'enable': T.Bool(),
            'max_attempts': T.Int(),
            'scan_timeout': T.Int(),
            }),
    T.Key('jenkins'):
        T.Dict({
            'user_id': T.String(),
            'api_token': T.String(),
            }),
    T.Key('gitlab_webhook_token'): T.String(),
    T.Key('server_url'): T.String(),
    T.Key('log_level'): T.String(),
    T.Key('host'): T.String(),
    T.Key('port'): T.Int(),
})
