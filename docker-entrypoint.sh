#!/bin/bash

set -e

#custom actions
case "$1" in
    server)
         python -m server.main -c /opt/app/config/server.yml
         exit 0
    ;;
    migrate)
        alembic -c /opt/app/config/alembic.ini upgrade head
        exit 0
    ;;
    init_example_data)
        python -m server.main -c /opt/app/config/server.yml --init-example-data
        exit 0
    ;;
esac

exec "$@"
