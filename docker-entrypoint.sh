#!/bin/bash

set -e


#custom actions
case "$1" in
    server)
         python -m server.main -c /opt/app/config/server.yml
    ;;
    migrate)
        alembic -c alembic.ini upgrade head
    ;;
esac


exec "$@"
