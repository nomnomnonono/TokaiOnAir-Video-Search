import os

import pandas as pd
import pytest
from apiclient.discovery import build
from apiclient.errors import HttpError
from dotenv import load_dotenv
from utils import ATTRS, getChannelPlaylistId, getVideoIds, getVideos

load_dotenv()
API_KEY = os.environ.get("API_KEY")
CHANNEL_ID = os.environ.get("CHANNEL_ID")


def test_env():
    assert API_KEY is not None
    assert CHANNEL_ID is not None


def test_youtube():
    youtube = build("youtube", "v3", developerKey=API_KEY)

    try:
        playlist_id = getChannelPlaylistId(youtube, CHANNEL_ID)
    except HttpError:
        pytest.fail("HttpError raised")

    video_ids = getVideoIds(youtube, playlist_id, is_local=False)
    assert len(video_ids) == 5
    assert isinstance(video_ids, list)
    assert isinstance(video_ids[0], str)

    video_data = getVideos(youtube, pd.DataFrame(video_ids, columns=["id"]))
    assert video_data.shape == (5, len(ATTRS) + 1)
    assert video_data.columns.tolist() == ["id"] + ATTRS
