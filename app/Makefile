.PHONY: deploy_app
deploy_app:
	gcloud run deploy ${APP_NAME} \
	--image ${LOCATION}-docker.pkg.dev/${GCP_PROJECT_ID}/${AR_REPOSITORY_NAME}/app:latest \
	--platform managed \
	--region ${LOCATION} \
	--add-cloudsql-instances ${GCP_PROJECT_ID}:${LOCATION}:${CLOUD_SQL_INSTANCE_NAME} \
	--set-env-vars INSTANCE_CONNECTION_NAME=${GCP_PROJECT_ID}:${LOCATION}:${CLOUD_SQL_INSTANCE_NAME},DB_USERNAME=${CLOUD_SQL_USER_NAME},DB_PASSWORD=${CLOUD_SQL_PASSWORD},DB_NAME=${CLOUD_SQL_DATABASE_NAME},RAILS_SERVE_STATIC_FILES=true \
	--allow-unauthenticated
