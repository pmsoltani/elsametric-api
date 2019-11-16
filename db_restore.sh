#!/usr/bin/env bash
# trap 'exit' ERR
set -e

if [ "${DB_RESTORE}" = "hib" ] && [ "${DB_DIALECT}" = "postgresql" ] ; then
    echo "inside if" \
    && cd /var/lib/postgresql \
    && pg_restore -U ${POSTGRES_USER} -d ${POSTGRES_DB} -v \
        $(find . -maxdepth 1 -type f -name "*.dump")
fi