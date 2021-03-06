#!/bin/bash

wsgi_entry_point="$1"
pid_file='/var/run/gunicorn/gunicorn.pid'

function stop_container {
    service nginx stop
    gunicorn_pid=$(cat ${pid_file})
    kill -TERM $(cat ${pid_file})
}

# Docker sends us a SIGTERM on 'docker stop'.
# This catches it and shuts down cleanly by calling the function above
trap stop_container SIGTERM

echo 'Installed handler' 1>&2

service nginx start

su -c "gunicorn --pid ${pid_file} --access-logfile /var/log/gunicorn/access.log --error-logfile /var/log/gunicorn/error.log --capture-output --bind 127.0.0.1:8000 '${wsgi_entry_point}'" mahiru &

wait

rm -f ${pid_file}
