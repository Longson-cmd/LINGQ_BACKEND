# Import YoutubeDL class from yt-dlp (used to extract subtitles)
from yt_dlp import YoutubeDL

# Import webvtt to parse .vtt subtitle files
import webvtt

# json is used to save the final timestamps to a .json file
import json

# tempfile lets us create a temporary folder that auto-deletes
import tempfile

# os is used to build file paths safely
import os

import glob
 

# from extract_data import get_lists_from_text



import json
import re
import unicodedata


# ======================================
# 1. Load and preprocess raw text
# ======================================

def clean_word(word: str) -> str:
    """
    Normalize and clean a single English word.

    Steps:
        - Lowercase and strip whitespace.
        - Normalize Unicode (NFKD) for consistent accents and symbols.
        - Replace smart quotes and various dash symbols.
        - Remove non-alphanumeric characters except apostrophes.

    Returns:
        str: cleaned word
    """
    w = word.lower().strip()

    w = unicodedata.normalize("NFKD", w)
    w = w.replace("’", "'").replace("–", "-").replace("—", "-")
    w = re.sub(r"[^\w\s']", "", w)
    return w


def get_sentence_lists(text: str):
    """
    Split raw text into lists of sentences.

    Args:
        text (str): the input text (may contain multiple paragraphs)

    Returns:
        tuple:
            - one_dimention_sentence_list (list[str]):
              flat list of all sentences across paragraphs
            - two_dimention_sentence_list (list[list[str]]):
              list of paragraphs, each containing a list of sentences
    """
    # Normalize newlines and trim whitespace
    t = text.replace('\r\n', '\n').replace('\r', '\n').strip()

    # Split by blank lines into paragraphs
    paras = re.split(r"\n+", t)
    paras = [para.strip() for para in paras if para.strip()]

    two_dimention_sentence_list = []

    # Process each paragraph
    for p in paras:
        # Clean spacing before punctuation
        p = re.sub(r"\s+([?.!])", r"\1", p)
        # Mark sentence endings temporarily with <S>
        p = re.sub(r"([!?.]+)", r"\1<S>", p)
        # Normalize multiple spaces/tabs
        p = re.sub(r"[ \t]+", " ", p)

        # Split paragraph into sentences
        sens = [s.strip() for s in p.split("<S>") if s.strip()]

        # Collect results
        two_dimention_sentence_list.append(sens)

    return  two_dimention_sentence_list



def get_lists_txt(txt_path):
    # ======================================
    # 2. Build cleaned reference data
    # ======================================
    # Read text file
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()
    # Generate sentence lists
    two_dimention_sentence_list = get_sentence_lists(text)
    list_id = []   # list of tuples: (word, (word_index, sentence_index))
    list_ref = []  # list of cleaned words only

    count_sentence = 0
    for p_idx, paragraph in enumerate(two_dimention_sentence_list):

        for s_idx, sentence in enumerate(paragraph):
            sentence_idx = count_sentence + s_idx
            for idx_in_s, word in enumerate(sentence.split()):
                list_id.append((word, p_idx, sentence_idx, idx_in_s))
                list_ref.append(clean_word(word))

        count_sentence += len(paragraph)
    print('total number of sentences', count_sentence)

    # Wrap into dictionary for export
    return list_ref, list_id



def get_lists_from_text(text):
    # Generate sentence lists
    two_dimention_sentence_list = get_sentence_lists(text)
    list_id = []   # list of tuples: (word, (word_index, sentence_index))
    list_ref = []  # list of cleaned words only

    count_sentence = 0
    for p_idx, paragraph in enumerate(two_dimention_sentence_list):

        for s_idx, sentence in enumerate(paragraph):
            sentence_idx = count_sentence + s_idx
            for idx_in_s, word in enumerate(sentence.split()):
                list_id.append((word, p_idx, sentence_idx, idx_in_s))
                list_ref.append(clean_word(word))

        count_sentence += len(paragraph)
    print('total number of sentences', count_sentence)

    # Wrap into dictionary for export
    return list_ref, list_id

    # ======================================
    # 3. Process Whisper transcription result
    # ======================================
 

def convert_time_stamp(time):
    hour_minute_second= [float(t) for  t in time.split(":")]
    seconds = hour_minute_second[0]*3600 + hour_minute_second[1]*60 + hour_minute_second[2]
    # return round(seconds, 2)
    return seconds

def convert_text(text):
    text = text.replace("\n", " ")
    return text



def get_timestamp(url):
    # Create a temporary directory
    # Everything inside this folder will be deleted automatically
    with tempfile.TemporaryDirectory() as tmpdir:
        
        chosen_lang = "en"
        # yt-dlp configuration options
        ydl_opts = {
            "skip_download": True,          # Do NOT download the video
            "writesubtitles": True,         # Allow subtitle download
            "writeautomaticsub": True,      # Allow auto-generated subtitles
            "subtitlesformat": "vtt",       # Force VTT format (important)
            "quiet": True,                  # Reduce console noise
            "no_warnings": True,
            # Output template:
            # Save subtitles inside the temp folder using video ID as filename
            # Example: <tmpdir>/ePMDcfFO9cw.en.vtt
            "subtitleslangs": [chosen_lang],
            "outtmpl": os.path.join(tmpdir, "%(id)s.%(lang)s.%(ext)s"),
        }
        with YoutubeDL(ydl_opts) as ydl:
            # Extract metadata AND download subtitles (because download=True)

            info = ydl.extract_info(url, download=True)      
        # Build the full path to the English VTT subtitle file
        # Example: C:/Temp/.../ePMDcfFO9cw.en.vtt
        # Find the actual VTT file yt-dlp created
        vtt_files = glob.glob(os.path.join(tmpdir, "*.vtt"))
        if not vtt_files:
            raise FileNotFoundError("No VTT subtitle file found")

        captions = webvtt.read(vtt_files[0])
        # Convert subtitles into a list of timestamp objects
        list_time_stamp = []
        subtitles_lines = []
        for c in captions:
            text_norm = convert_text(c.text)
            list_time_stamp.append({
                "start": convert_time_stamp(c.start),   # Start time (HH:MM:SS.mmm)
                "end": convert_time_stamp(c.end),       # End time (HH:MM:SS.mmm)
                "text": text_norm    # Subtitle text
            })
            subtitles_lines.append(text_norm)
    subtitles = "\n".join(subtitles_lines)
    list_ref, list_id = get_lists_from_text(subtitles)
    json_dict = {"list_ref": list_ref, "list_id": list_id}

    return list_time_stamp, json_dict, info['id'], info.get("title").strip().replace(" ", "_")
    

def get_thumbnail_url(url):
    with YoutubeDL({"quiet": True, "no_warnings":True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("thumbnail")
    
    

if __name__ == "__main__":
    # url = "https://www.youtube.com/watch?v=ePMDcfFO9cw"
    url = "https://www.youtube.com/watch?v=uKN5I-Mtgzs"

    list_time_stamp , json_dict, id, title = get_timestamp(url)
    print("title", title)
    with open(f"youtube.json", "w", encoding="utf-8") as f:
        json.dump(list_time_stamp, f, indent=2, ensure_ascii=False)

