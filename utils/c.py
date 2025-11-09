import json
import sys
from pydub import AudioSegment
import simpleaudio as sa


i = 2
# ---- Load JSON file ----
json_file = rf"C:\Users\PC\Desktop\practise\lingq\media\timestamps\test@example.com\lesson_{i}_timestamp.json"
with open(json_file, "r", encoding="utf-8") as file:
    sentence_timestamps_two_dimetion = json.load(file)

sentence_timestamps = []
for sublist in sentence_timestamps_two_dimetion:
    for item in sublist:
        sentence_timestamps.append(item)
if not sentence_timestamps:
    raise ValueError("❌ No timestamps found in checkaudio.json")

# ---- Get index from command line ----
if len(sys.argv) < 2:
    print(f"Usage: python c.py <index>")
    sys.exit(1)

try:
    idx = int(sys.argv[1])
except ValueError:
    print("⚠️ Index must be an integer.")
    sys.exit(1)

if not (0 <= idx < len(sentence_timestamps)):
    print(f"⚠️ Index out of range. Valid range: 0–{len(sentence_timestamps)-1}")
    sys.exit(1)

# ---- Select the sentence ----
s = sentence_timestamps[idx]
start = int(s["start"])
end = s["end"]
text = s["text"]

print(f"\n▶️ Playing sentence {idx}:")
print(f"Text : {text}")
print(f"Start: {start}s, End: {end}s")

# ---- Load and play audio ----
# Load the audio file "test{i}.mp3" using pydub's AudioSegment class
# The 'format="mp3"' argument tells it the file type explicitly.
audio_path = rf"C:\Users\PC\Desktop\practise\lingq\media\audios\test@example.com\test{i}.mp3"
audio = AudioSegment.from_file(audio_path, format="mp3")

# Extract a portion of the audio from 'start' to 'end' (in seconds)
# pydub works in milliseconds, so multiply by 1000.
segment = audio[start * 1000 : end * 1000]

# Play the selected audio segment using simpleaudio
# 'segment.raw_data' gives the raw PCM audio bytes
# 'num_channels' = mono or stereo, 'bytes_per_sample' = sample width (e.g., 2 bytes)
# 'sample_rate' = playback speed in Hz
play_obj = sa.play_buffer(
    segment.raw_data,
    num_channels=segment.channels,
    bytes_per_sample=segment.sample_width,
    sample_rate=segment.frame_rate
)

# Wait until the playback finishes before continuing the script
play_obj.wait_done()

print("\n✅ Done playing.")
