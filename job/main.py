import os

import pandas as pd
import sqlalchemy
from apiclient.discovery import build
from dotenv import load_dotenv
from google.cloud import storage
from google.cloud.sql.connector import Connector
from utils import COLUMNS, getChannelPlaylistId, getVideoIds, getVideos

load_dotenv()
API_KEY = os.environ.get("API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
DATA_BUCKET = os.environ.get("DATA_BUCKET")


def getconn():
    conn = Connector().connect(
        f"{os.environ.get('GCP_PROJECT_ID')}:{os.environ.get('LOCATION')}:{os.environ.get('CLOUD_SQL_INSTANCE_NAME')}",
        "pymysql",
        user="root",
        password=os.environ.get("CLOUD_SQL_PASSWORD"),
        db=os.environ.get("CLOUD_SQL_DATABASE_NAME"),
    )
    return conn


def main():
    youtube = build("youtube", "v3", developerKey=API_KEY)
    playlist_id = getChannelPlaylistId(youtube, CHANNEL_ID)
    video_ids = getVideoIds(youtube, playlist_id)
    video_data = getVideos(youtube, pd.DataFrame(video_ids, columns=["id"]))
    video_data.where(video_data.notna(), None, inplace=True)

    # Upload video data to GCS
    client = storage.Client()
    bucket = client.bucket(DATA_BUCKET.lstrip("gs://"))
    blob = bucket.blob("videos.csv")
    blob.upload_from_string(video_data.to_csv(index=False), "text/csv")

    # Upload video data to Cloud SQL
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
    )
    with pool.connect() as db_conn:
        insert_stmt = sqlalchemy.text(
            f"INSERT INTO {os.environ.get('CLOUD_SQL_TABLE_NAME')} (ID, TITLE, DESCRIPTION, THUMBNAIL, YEAR, MONTH, DAY, VIEWCOUNT, LIKECOUNT) VALUES (:id, :title, :description, :thumbnail, :year, :month, :day, :viewcount, :likecount)"
        )
        search_stmt = sqlalchemy.text(
            f"SELECT COUNT(*) FROM {os.environ.get('CLOUD_SQL_TABLE_NAME')} WHERE ID = :id"
        )
        update_stmt = sqlalchemy.text(
            f"UPDATE {os.environ.get('CLOUD_SQL_TABLE_NAME')} SET TITLE = :title, DESCRIPTION = :description, THUMBNAIL = :thumbnail, YEAR = :year, MONTH = :month, DAY = :day, VIEWCOUNT = :viewcount, LIKECOUNT = :likecount WHERE ID = :id"
        )

        for i in range(len(video_data)):
            # if video is already in database, update it, else insert it
            if (
                db_conn.execute(
                    search_stmt, parameters={"id": video_data["id"][i]}
                ).fetchone()[0]
                > 0
            ):
                db_conn.execute(update_stmt, parameters=video_data.iloc[i].to_dict())
                print(f"Updated video#{video_data['id'][i]}")
            else:
                db_conn.execute(insert_stmt, parameters=video_data.iloc[i].to_dict())
                print(f"Inserted video#{video_data['id'][i]}")

        db_conn.commit()


if __name__ == "__main__":
    main()
