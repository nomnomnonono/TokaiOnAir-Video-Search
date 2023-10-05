.PHONY: format
format:
	poetry run pysen run format

.PHONY: lint
lint:
	poetry run pysen run lint

.PHONY: test
test:
	poetry run pytest tests/*

.PHONY: install
install:
	poetry install

## Cloud Run Job
.PHONY: deploy_job
deploy_job:
	gcloud run jobs deploy ${JOB_NAME} \
	--image ${LOCATION}-docker.pkg.dev/${GCP_PROJECT_ID}/${AR_REPOSITORY_NAME}/job:latest \
	--region ${LOCATION} \
	--set-cloudsql-instances=${CLOUD_SQL_INSTANCE_NAME}

.PHONY: exec_job
exec_job:
	gcloud run jobs execute ${JOB_NAME} --region ${LOCATION}

.PHONY: create_scheduler
create_scheduler:
	gcloud scheduler jobs create http ${SCHEDULER_NAME} \
	--location ${LOCATION} \
	--schedule="0 0 * * *" \
	--uri="https://${LOCATION}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${GCP_PROJECT_ID}/jobs/${JOB_NAME}:run" \
	--http-method POST \
	--oauth-service-account-email=${SERVICE_ACCOUNT_EMAIL}

## Cloud SQL
.PHONY: setup_cloudsql
setup_cloudsql:
	make create_cloudsql_instance
	make create_cloudsql_database
	make set_password_cloudsql_instance
	gsutil mb ${DATA_BUCKET}
	poetry run python main.py --is_local

.PHONY: create_cloudsql_instance
create_cloudsql_instance:
	gcloud sql instances create ${CLOUD_SQL_INSTANCE_NAME} \
    --region ${LOCATION} \
    --tier db-f1-micro

.PHONY: create_cloudsql_database
create_cloudsql_database:
	gcloud sql databases create ${CLOUD_SQL_DATABASE_NAME} \
	--instance ${CLOUD_SQL_INSTANCE_NAME}

.PHONY: set_password_cloudsql_instance
set_password_cloudsql_instance:
	gcloud sql users set-password root \
	--host=% \
	--instance ${CLOUD_SQL_INSTANCE_NAME} \
	--password ${CLOUD_SQL_PASSWORD}

.PHONY: import_csv_to_cloudsql
import_csv_to_cloudsql:
	gsutil iam ch serviceAccount:${SERVICE_ACCOUNT_EMAIL}:roles/storage.objectAdmin ${DATA_BUCKET}
	gcloud sql import csv ${CLOUD_SQL_INSTANCE_NAME} ${DATA_BUCKET}/videos.csv \
	--database=${CLOUD_SQL_DATABASE_NAME} \
	--table=${CLOUD_SQL_TABLE_NAME}
