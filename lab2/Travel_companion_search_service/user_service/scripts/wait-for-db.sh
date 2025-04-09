#!/bin/sh

# Параметры подключения
HOST="users_db"
PORT="5433"
USER="practical-proj"
DB="companion_search"
PASSWORD="1"
TIMEOUT=60

echo "Ожидание PostgreSQL на $HOST:$PORT..."

while ! PGPASSWORD=$PASSWORD pg_isready -h $HOST -p $PORT -U $USER -d $DB -t 1; do
    TIMEOUT=$((TIMEOUT-1))
    if [ $TIMEOUT -eq 0 ]; then
        echo "Таймаут подключения к PostgreSQL!"
        exit 1
    fi
    sleep 1
done

echo "PostgreSQL доступен, продолжаем запуск..."
exec "$@"