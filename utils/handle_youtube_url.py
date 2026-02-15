# Import YoutubeDL class from yt-dlp (used to extract subtitles)
# from yt_dlp import YoutubeDL

# Import webvtt to parse .vtt subtitle files
# import webvtt

# json is used to save the final timestamps to a .json file
import json

# tempfile lets us create a temporary folder that auto-deletes
import tempfile

# os is used to build file paths safely
import os

import glob
 
from utils.extract_data import get_lists_from_text
# from extract_data import get_lists_from_text


def convert_time_stamp(time):
    hour_minute_second= [float(t) for  t in time.split(":")]
    seconds = hour_minute_second[0]*3600 + hour_minute_second[1]*60 + hour_minute_second[2]
    # return round(seconds, 2)
    return seconds

def convert_text(text):
    text = text.replace("\n", " ")
    return text


# def get_timestamp(url):
#     # Create a temporary directory
#     # Everything inside this folder will be deleted automatically
#     with tempfile.TemporaryDirectory() as tmpdir:
        
#         chosen_lang = "en"
#         # yt-dlp configuration options
#         ydl_opts = {
#             "skip_download": True,          # Do NOT download the video
#             "writesubtitles": True,         # Allow subtitle download
#             "writeautomaticsub": True,      # Allow auto-generated subtitles
#             "subtitlesformat": "vtt",       # Force VTT format (important)
#             "quiet": True,                  # Reduce console noise
#             "no_warnings": True,
#             # Output template:
#             # Save subtitles inside the temp folder using video ID as filename
#             # Example: <tmpdir>/ePMDcfFO9cw.en.vtt
#             "subtitleslangs": [chosen_lang],
#             "outtmpl": os.path.join(tmpdir, "%(id)s.%(lang)s.%(ext)s"),
#         }
#         with YoutubeDL(ydl_opts) as ydl:
#             # Extract metadata AND download subtitles (because download=True)

#             info = ydl.extract_info(url, download=True)      
#         # Build the full path to the English VTT subtitle file
#         # Example: C:/Temp/.../ePMDcfFO9cw.en.vtt
#         # Find the actual VTT file yt-dlp created
#         vtt_files = glob.glob(os.path.join(tmpdir, "*.vtt"))
#         if not vtt_files:
#             raise FileNotFoundError("No VTT subtitle file found")

#         captions = webvtt.read(vtt_files[0])
#         # Convert subtitles into a list of timestamp objects
#         list_time_stamp = []
#         subtitles_lines = []
#         for c in captions:
#             text_norm = convert_text(c.text)
#             list_time_stamp.append({
#                 "start": convert_time_stamp(c.start),   # Start time (HH:MM:SS.mmm)
#                 "end": convert_time_stamp(c.end),       # End time (HH:MM:SS.mmm)
#                 "text": text_norm    # Subtitle text
#             })
#             subtitles_lines.append(text_norm)
#     subtitles = "\n".join(subtitles_lines)
#     list_ref, list_id = get_lists_from_text(subtitles)
#     json_dict = {"list_ref": list_ref, "list_id": list_id}

#     return list_time_stamp, json_dict, info['id'], info.get("title").strip().replace(" ", "_")


# def get_thumbnail_url(url):
#     with YoutubeDL({"quiet": True, "no_warnings":True}) as ydl:
#         info = ydl.extract_info(url, download=False)
#         return info.get("thumbnail")
      
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import requests


def extract_video_id(url: str):
    parsed = urlparse(url)

    if parsed.hostname in ("youtu.be",):
        return parsed.path[1:]

    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]

    raise ValueError("Invalid YouTube URL")

def get_thumbnail_url(url):
    video_id = extract_video_id(url)
    return f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"


def get_timestamp(url):
    video_id = extract_video_id(url)

    # 1️⃣ Get transcript safely (no bot trigger)
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])

    list_time_stamp = []
    subtitles_lines = []

    for entry in transcript:
        text_norm = convert_text(entry["text"])

        list_time_stamp.append({
            "start": entry["start"],
            "end": entry["start"] + entry["duration"],
            "text": text_norm
        })

        subtitles_lines.append(text_norm)

    subtitles = "\n".join(subtitles_lines)

    list_ref, list_id = get_lists_from_text(subtitles)
    json_dict = {"list_ref": list_ref, "list_id": list_id}

    # 2️⃣ Get title safely using oEmbed (no yt-dlp)
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    response = requests.get(oembed_url, timeout=10)
    response.raise_for_status()
    youtube_title = response.json().get("title", "youtube_video")

    return list_time_stamp, json_dict, video_id, youtube_title.strip().replace(" ", "_")

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=ePMDcfFO9cw"

    list_time_stamp , json_dict, id, title = get_timestamp(url)
    print("title", title)
    with open(f"youtube.json", "w", encoding="utf-8") as f:
        json.dump(list_time_stamp, f, indent=2, ensure_ascii=False)


