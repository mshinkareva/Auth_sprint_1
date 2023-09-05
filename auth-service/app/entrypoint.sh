#!/bin/sh


echo "Waiting for Redis..."

while ! nc -z $REDIS_HOST $REDIS_PORT; do
  sleep 1
done

echo "Redis started"


echo "Waiting for PG..."

while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 10
done

echo "PG started"

alembic upgrade head

gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app

exec "$@"
