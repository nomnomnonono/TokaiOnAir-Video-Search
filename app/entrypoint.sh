#!/bin/sh

/cloud_sql_proxy -instances=$GCP_PROJECT_ID:$LOCATION:$CLOUD_SQL_INSTANCE_NAME=tcp:3306 &

RUN bundle exec rake assets:precompile
bin/rails db:migrate RAILS_ENV=production
bin/rails db:seed RAILS_ENV=production

exec "$@"
