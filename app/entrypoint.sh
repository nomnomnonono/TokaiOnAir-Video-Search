#!/bin/sh

bundle exec rake assets:precompile
#bin/rails db:migrate RAILS_ENV=production
#bin/rails db:seed RAILS_ENV=production

exec "$@"
