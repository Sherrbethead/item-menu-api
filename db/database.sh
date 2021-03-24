#!/bin/bash
CONFIG_PY="main"
BACKUP_DB=true

# присваиваем значения для сервера, имени пользователя, паролю и названию БД из конфига сервиса
DB_HOST=$(python3 -c "from ${CONFIG_PY} import settings; print(settings.POSTGRES.host)")
DB_USER=$(python3 -c "from ${CONFIG_PY} import settings; print(settings.POSTGRES.user)")
DB_NAME=$(python3 -c "from ${CONFIG_PY} import settings; print(settings.POSTGRES.database)")
export PGPASSWORD=$(python3 -c "from ${CONFIG_PY} import settings; print(settings.POSTGRES.password)")

# проверяем наличие бд
DB=$(psql -h "${DB_HOST}" -U "${DB_USER}" -t -d postgres -c "SELECT datname FROM pg_database WHERE datname='${DB_NAME}'")
# если нет, то создаем новую
if [ "$DB" != "" ]; then
        # закрываем все активные сессии бд
        psql -h "${DB_HOST}" -U "${DB_USER}" -c "SELECT pg_terminate_backend(pg_stat_activity.pid)
                                                 FROM pg_stat_activity
                                                 WHERE pg_stat_activity.datname = '${DB_NAME}'
                                                 AND pid <> pg_backend_pid();"

        # удаляем бд
        if $BACKUP_DB; then
                DATE=$(date +%s);
                psql -h "${DB_HOST}" -U "${DB_USER}" -c "ALTER DATABASE ${DB_NAME} RENAME TO ${DB_NAME}_$DATE;"
        else
                psql -h "${DB_HOST}" -U "${DB_USER}" -c "DROP DATABASE ${DB_NAME};"
        fi
fi

# создаем новую бд
psql -h "${DB_HOST}" -U "${DB_USER}" -c "CREATE DATABASE ${DB_NAME};"

# накатываем миграции
alembic upgrade head
