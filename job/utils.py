COLUMNS = [
    "title",
    "description",
    "thumbnail",
    "year",
    "month",
    "day",
    "viewCount",
    "likeCount",
]


def getChannelPlaylistId(youtube, channel_id):
    channel = (
        youtube.channels().list(part="snippet,contentDetails", id=channel_id).execute()
    )
    item = channel["items"][0]
    playlist_id = item["contentDetails"]["relatedPlaylists"]["uploads"]
    return playlist_id


def getVideoIds(youtube, playlist_id, is_prod=True, page_token=None):
    items_info = (
        youtube.playlistItems()
        .list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50 if is_prod else 5,
            pageToken=page_token,
        )
        .execute()
    )
    video_ids = list(
        map(lambda item: item["contentDetails"]["videoId"], items_info["items"])
    )

    if is_prod and "nextPageToken" in items_info:
        video_ids.extend(
            getVideoIds(youtube, playlist_id, is_prod, items_info["nextPageToken"])
        )

    return video_ids


def getVideos(youtube, video_data):
    for idx in range(len(video_data)):
        video_info = (
            youtube.videos()
            .list(part="snippet,statistics", id=video_data.loc[idx, "id"])
            .execute()["items"][0]
        )

        date_dict = process_date(video_info["snippet"]["publishedAt"])

        for attr in COLUMNS:
            try:
                if attr == "thumbnail":
                    video_data.loc[idx, attr] = video_info["snippet"]["thumbnails"][
                        "default"
                    ]["url"]
                elif attr in ["viewCount", "likeCount"]:
                    video_data.loc[idx, attr] = video_info["statistics"][attr]
                elif attr in ["year", "month", "day"]:
                    video_data.loc[idx, attr] = date_dict[attr]
                else:
                    video_data.loc[idx, attr] = video_info["snippet"][attr]
            except Exception:
                print(
                    f"Error: Unable to get {attr} in video#{video_data.loc[idx, 'id']}"
                )

    return video_data


def process_date(date):
    year, month, other = date.split("-")
    return {"year": year, "month": month, "day": other.split("T")[0]}
