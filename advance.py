import streamlit as st
import requests
from datetime import datetime, timedelta
import isodate

# -----------------------------
# 🔑 Your YouTube API Key
# -----------------------------
API_KEY = "AIzaSyAuJcNJ2-by70P-nhfHc1LyhgWc_9EfQNk"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# -----------------------------
# Helper: Convert ISO duration to minutes
# -----------------------------
def get_minutes(duration_str):
    duration = isodate.parse_duration(duration_str)
    return duration.total_seconds() / 60

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🔎 YouTube Crime Research Tool")

# Input Fields
days = st.number_input("Search videos from last X days:", min_value=1, max_value=30, value=7)
min_subs = st.number_input("Min Subscribers:", min_value=0, max_value=1000000, value=0, step=1000)
max_subs = st.number_input("Max Subscribers:", min_value=0, max_value=1000000, value=20000, step=1000)
min_duration = st.number_input("Min Video Duration (minutes):", min_value=0, max_value=600, value=0)
max_duration = st.number_input("Max Video Duration (minutes):", min_value=1, max_value=600, value=60)

# Crime Keywords (popular viral)
keywords = [
    "True Crime Story", "Murder Mystery", "Unsolved Crime", "Missing Person Case",
    "Serial Killer Documentary", "Crime Investigation", "Real Crime Story",
    "Crime Confession", "Forensic Investigation", "Reddit Crime Story",
    "Crime Patrol", "Crime Scene Analysis", "Famous Criminal Cases",
    "Crime Drama Documentary", "Cold Case Solved", "Shocking Crime Story",
    "Prison Confession", "Dark Crime Story", "True Detective Story"
]

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"🔍 Searching for keyword: {keyword}")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "items" not in data or not data["items"]:
                st.warning(f"No videos found for keyword: {keyword}")
                continue

            videos = data["items"]
            video_ids = [v["id"]["videoId"] for v in videos if "id" in v and "videoId" in v["id"]]
            channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v and "channelId" in v["snippet"]]

            if not video_ids or not channel_ids:
                continue

            # Video statistics + duration
            stats_params = {"part": "statistics,contentDetails", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()
            if "items" not in stats_data or not stats_data["items"]:
                continue

            # Channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()
            if "items" not in channel_data or not channel_data["items"]:
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Collect results
            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                duration_str = stat["contentDetails"]["duration"]
                duration_min = get_minutes(duration_str)

                if min_subs <= subs <= max_subs and min_duration <= duration_min <= max_duration:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs,
                        "Duration (min)": round(duration_min, 2)
                    })

        # Display results
        if all_results:
            st.success(f"Found {len(all_results)} videos matching your filters! 🎯")
            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Subscribers:** {result['Subscribers']}  \n"
                    f"**Duration:** {result['Duration (min)']} min"
                )
                st.write("---")
        else:
            st.warning("No results found with these filters.")

    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")
