import argparse
import os

import pandas as pd
import sqlalchemy
from apiclient.discovery import build
from dotenv import load_dotenv
from google.cloud.sql.connector import Connector
from utils import getChannelPlaylistId, getVideoIds, getVideos

load_dotenv()
API_KEY = os.environ.get("API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
DATA_BUCKET = os.environ.get("DATA_BUCKET")


def getconn():
    conn =  Connector().connect(
        f"{os.environ.get('GCP_PROJECT_ID')}:{os.environ.get('LOCATION')}:{os.environ.get('CLOUD_SQL_INSTANCE_NAME')}",
        "pymysql",
        user="root",
        password=os.environ.get("CLOUD_SQL_PASSWORD"),
        db=os.environ.get("CLOUD_SQL_DATABASE_NAME")
    )
    return conn


def main(args):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    playlist_id = getChannelPlaylistId(youtube, CHANNEL_ID)
    video_ids = getVideoIds(youtube, playlist_id, args.is_local)
    video_data = getVideos(youtube, pd.DataFrame(video_ids, columns=["id"]))
    video_data.where(video_data.notna(), None, inplace=True)

    if args.is_local:
        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket(DATA_BUCKET.lstrip("gs://"))
        blob = bucket.blob("videos.csv")
        blob.upload_from_string(video_data.to_csv(index=False), "text/csv")
    else:
        pool = sqlalchemy.create_engine(
            "mysql+pymysql://",
            creator=getconn,
        )
        with pool.connect() as db_conn:
            insert_stmt = sqlalchemy.text(
                f"INSERT INTO {os.environ.get('CLOUD_SQL_TABLE_NAME')} (ID, TITLE, DESCRIPTION, THUMBNAIL, PUBLISHEDAT, VIEWCOUNT, LIKECOUNT) VALUES (:id, :title, :description, :thumbnail, :publishedAt, :viewCount, :likeCount)"
            )

            # Insert entries into table
            for i in range(len(video_data)):
                try:
                    db_conn.execute(insert_stmt, parameters=video_data.iloc[i].to_dict())
                    print(f"Successly inserted Video: {video_data.iloc[i]['title']}")
                except Exception as e:
                    print("Error", e)

            db_conn.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--is_local", action="store_true")
    args = parser.parse_args()
    main(args)
