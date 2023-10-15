#!/bin/sh

/cloud_sql_proxy -instances=$GCP_PROJECT_ID:$LOCATION:$CLOUD_SQL_INSTANCE_NAME=tcp:3306 &

exec "$@"
