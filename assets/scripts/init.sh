#!/bin/bash

service supervisor start
service nginx start


while sleep 60; do
    echo "### Checking if service is up... ###"
    echo "[i] Check if app is running"
    gun_id=$(ps -ef | grep "gunicorn" | grep -v grep | awk '{print $2; exit}')
    if [ $gun_id ]; then
        echo "App is running!"
    else
        echo "App was not running. Attempting to re-start..."
        service supervisor force-reload
        service supervisor start
    fi

    echo "[i] Check proxy is running"
    proxy_id=$(ps -ef | grep "nginx" | grep -v grep | awk '{print $2; exit}')
    if [ $proxy_id ]; then
        echo "Proxy is running!"
    else
        echo "Nginx has stopped running. Restarting..."
        service nginx start
    fi

    echo "All checks done. Re-checking in 60s..."
done