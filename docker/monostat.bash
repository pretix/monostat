#!/bin/bash
cd /src
export DATA_DIR=/data/
export HOME=/src

AUTOMIGRATE=${AUTOMIGRATE:-yes}
NUM_WORKERS_DEFAULT=$((2 * $(nproc)))
export NUM_WORKERS=${NUM_WORKERS:-$NUM_WORKERS_DEFAULT}

if [ ! -d /data/logs ]; then
    mkdir /data/logs;
fi
if [ ! -d /data/media ]; then
    mkdir /data/media;
fi

if [ "$AUTOMIGRATE" != "skip" ]; then
  python3 -m monostat migrate --noinput
fi

if [ "$1" == "all" ]; then
    exec sudo -E /usr/bin/supervisord -n -c /etc/supervisord.all.conf
fi

if [ "$1" == "web" ]; then
    exec gunicorn monostat.wsgi \
        --name monostat \
        --workers $NUM_WORKERS \
        --max-requests 1200 \
        --max-requests-jitter 50 \
        --log-level=info \
        --bind=unix:/tmp/monostat.sock
fi

if [ "$1" == "taskworker" ]; then
    exec python3 -m monostat run_huey --workers $NUM_WORKERS
fi

exec python3 -m monostat "$@"
