# CloudRun Job to Collect TokaiOnAir Video Data

## Requirements
- Poetry
- gcloud CLI
- docker compose

## Setup
### Install Dependencies
```bash
$ make install
```

### Environmental Variables
```bash
$ vi .env
$ cp .env job/
```

- 以下の情報を記入＋環境変数としてexportしておく
```bash
GCP_PROJECT_ID=your project id
LOCATION=asia-northeast1
AR_REPOSITORY_NAME=artifact registory repository name
JOB_NAME=cloud run job name
SCHEDULER_NAME=cloud scheduler name
CLOUD_SQL_INSTANCE_NAME=cloud sql instance name
CLOUD_SQL_DATABASE_NAME=cloud sql database name
CLOUD_SQL_USER_NAME=cloud sql user name
CLOUD_SQL_PASSWORD=cluod sql password
API_KEY=API key for YouTube Data API v3
CHANNEL_ID=UCutJqz56653xV2wwSvut_hQ
```

### GCP Authentification
```bash
$ gcloud auth login
$ gcloud config set project $GCP_PROJECT_ID
$ gcloud components install pubsub-emulator
```

## Cloud SQL
### Create 
```bash
$ make setup_cloudsql
```

### Create Tabel from Cloud Shell
Cloud SQLのWebページからCloud Shellを開いて、以下のコマンドを実行する
```sql
CREATE TABLE ${CLOUD_SQL_DATABASE_NAME}.${CLOUD_SQL_TABLE_NAME} (
    ID VARCHAR(50) NOT NULL,
    TITLE TEXT,
    DESCRIPTION TEXT,
    THUMBNAIL TEXT,
    PUBLISHEDAT TEXT,
    VIEWCOUNT INT,
    LIKECOUNT INT,
    PRIMARY KEY (ID)
);
```

### Upload CSV to Cloud SQL
以下のコマンドを実行した出力から、`serviceAccountEmailAddress`フィールドを探す
```bash
$ gcloud sql instances describe ${CLOUD_SQL_INSTANCE_NAME}
```
フィールドの値を`.env`ファイルに追加、環境変数に反映
```bash
$ SERVICE_ACCOUNT_EMAIL=service account email address
```
Cloud SQLに動画データの反映
```bash
$ make import_csv_to_cloudsql
```

## Build & Push Docker Image
```bash
$ gcloud auth configure-docker asia-northeast1-docker.pkg.dev
$ gcloud artifacts repositories create $AR_REPOSITORY_NAME --location=$LOCATION --repository-format=docker
$ docker compose build
$ docker compose push
```

## Cloud Run Job to Get YouTube Data
### Deploy
```bash
$ make deploy_job
```

### Create Scheduler
```bash
$ make create_scheduler
```
