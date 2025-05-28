#! /usr/bin/env bash

sleep 5 && \
    echo "Running database migrations..." && \
    alembic upgrade head && \
    echo "Database migration completed" && \
    echo "Starting tests..." && \
    pytest --maxfail=1 --disable-warnings -q -vv && \
    echo "Starting the application..." && \
    gunicorn fast:app --bind 0.0.0.0:8000 --timeout 900
