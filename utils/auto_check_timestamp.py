import json
import time
from pydub import AudioSegment
import simpleaudio as sa

# ---- Settings ----
i = 3
pause_between_sentences = 1  # seconds

# ---- Load JSON file ----
json_file = rf"C:\Users\PC\Desktop\practise\lingq\media\timestamps\test@example.com\lesson_{i}_timestamp.json"
with open(json_file, "r", encoding="utf-8") as file:
    sentence_timestamps_two_dimetion = json.load(file)

# Flatten 2D list
sentence_timestamps = [item for sublist in sentence_timestamps_two_dimetion for item in sublist]

if not sentence_timestamps:
    raise ValueError("❌ No timestamps found in the JSON file.")

# ---- Load audio once ----
audio_path = rf"C:\Users\PC\Desktop\practise\lingq\media\audios\test@example.com\test{i}.mp3"
audio = AudioSegment.from_file(audio_path, format="mp3")

# ---- Iterate through all sentences ----
for idx, s in enumerate(sentence_timestamps):
    start = s.get("start")
    end = s.get("end")
    text = s.get("text", "")
    print(f"\n▶️ Playing sentence {idx + 1}/{len(sentence_timestamps)}")
    print(f"Text : {text}")
    print(f"Start: {start}s, End: {end}s")
    # Skip invalid entries
    if start is None or end is None:
        print(f"⚠️ Skipping sentence {idx + 1}: missing timestamps")
        continue

    start = int(start)
    

    segment = audio[start * 1000 : end * 1000]

    play_obj = sa.play_buffer(
        segment.raw_data,
        num_channels=segment.channels,
        bytes_per_sample=segment.sample_width,
        sample_rate=segment.frame_rate
    )
    play_obj.wait_done()
    time.sleep(pause_between_sentences)

print("\n✅ All sentences played successfully.")
