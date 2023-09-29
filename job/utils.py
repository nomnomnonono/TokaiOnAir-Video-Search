ATTRS = ["title", "description", "thumbnail", "publishedAt", "viewCount", "likeCount"]


def getChannelPlaylistId(youtube, channel_id):
    channel = (
        youtube.channels().list(part="snippet,contentDetails", id=channel_id).execute()
    )
    item = channel["items"][0]
    playlist_id = item["contentDetails"]["relatedPlaylists"]["uploads"]
    return playlist_id


def getVideoIds(youtube, playlist_id, is_local, page_token=None):
    items_info = (
        youtube.playlistItems()
        .list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50 if is_local else 5,
            pageToken=page_token,
        )
        .execute()
    )
    video_ids = list(
        map(lambda item: item["contentDetails"]["videoId"], items_info["items"])
    )

    if is_local and "nextPageToken" in items_info:
        video_ids.extend(
            getVideoIds(youtube, playlist_id, is_local, items_info["nextPageToken"])
        )

    return video_ids


def getVideos(youtube, video_data):
    for idx in range(len(video_data)):
        video_info = (
            youtube.videos()
            .list(part="snippet,statistics", id=video_data.loc[idx, "id"])
            .execute()["items"][0]
        )
        for attr in ATTRS:
            try:
                if attr == "thumbnail":
                    video_data.loc[idx, attr] = video_info["snippet"]["thumbnails"][
                        "default"
                    ]["url"]
                elif attr in ["viewCount", "likeCount"]:
                    video_data.loc[idx, attr] = video_info["statistics"][attr]
                else:
                    video_data.loc[idx, attr] = video_info["snippet"][attr]
            except:
                print(
                    f"Error: Unable to get {attr} in video#{video_data.loc[idx, 'id']}"
                )
    return video_data
