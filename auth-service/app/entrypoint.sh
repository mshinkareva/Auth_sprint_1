#!/bin/sh


echo "Waiting for Redis..."

while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 1
done

echo "Redis started"


echo "Waiting for PG..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "PG started"

alembic upgrade head

gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app

exec "$@"