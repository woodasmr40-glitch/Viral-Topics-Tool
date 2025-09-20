import streamlit as st
import requests
from datetime import datetime, timedelta

# -----------------------------
# 🔑 AIzaSyAuJcNJ2-by70P-nhfHc1LyhgWc_9EfQNk
# -----------------------------
API_KEY = "Enter your API Key here"

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# -----------------------------
# 🎬 Streamlit UI
# -----------------------------
st.title("YouTube Viral Topics Tool - Health Niche")

# Inputs
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# -----------------------------
# 🩺 Health Keywords
# -----------------------------
keywords = [
    "Home Remedies for Health", "Weight Loss Tips", "Fitness Motivation", "Yoga for Beginners",
    "Healthy Diet Plan", "Intermittent Fasting", "Mental Health Awareness", "Depression Treatment",
    "Diabetes Control Naturally", "Heart Health Tips", "Skincare Routine", "Hair Fall Treatment",
    "Healthy Lifestyle", "Workout at Home", "Nutrition Advice", "Best Superfoods",
    "Meditation Benefits", "Stress Relief Techniques", "Sleep Better Naturally", "Boost Immunity"
]

# -----------------------------
# 🔎 Fetch Data Button
# -----------------------------
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
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                continue

            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                # ✅ Filter: only channels under 20,000 subs
                if subs < 20000:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # -----------------------------
        # 📊 Show Results
        # -----------------------------
        if all_results:
            st.success(f"Found {len(all_results)} results 🎉")
            for result in all_results:
                st.markdown(
                    f"**Title:** {result['Title']}  \n"
                    f"**Description:** {result['Description']}  \n"
                    f"**URL:** [Watch Video]({result['URL']})  \n"
                    f"**Views:** {result['Views']}  \n"
                    f"**Subscribers:** {result['Subscribers']}"
                )
                st.write("---")
        else:
            st.warning("No results found for channels with fewer than 20,000 subscribers.")

    except Exception as e:
        st.error(f"⚠️ An error occurred: {e}")
