
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
                list_id.append((word, (p_idx, sentence_idx, idx_in_s)))
                list_ref.append(clean_word(word))

        count_sentence += len(paragraph)
    print('total number of sentences', count_sentence)

    # Wrap into dictionary for export
    return list_ref, list_id

    # ======================================
    # 3. Process Whisper transcription result
    # ======================================
def get_lists_whisper(whisper_path):

    # Load Whisper JSON file
    with open(whisper_path, encoding='utf-8') as f:
        data = json.load(f)['segments']

    whisper_wordtimestamp = []  # list of word timestamp dictionaries
    whisper = []                # list of cleaned words

    for item in data:
        start_sentence = item["start"]
        end_sentence = item["end"]
        list_words = [clean_word(w) for w in item["text"].split()]

        # If Whisper provides a segment with no words, assign a default gap
        if len(list_words) != 0:
            gap = (end_sentence - start_sentence) / len(list_words)
        else:
            gap = 1

        # Distribute timestamps evenly across words in the segment
        for i, word in enumerate(list_words):
            whisper.append(word)
            whisper_wordtimestamp.append(
                {
                    "word": word,
                    "start": round(start_sentence + gap * i, 2),
                    "end": round(start_sentence + gap * (i + 1), 2),
                }
            )

    return  whisper_wordtimestamp, whisper


if __name__ == "__main__":
    import json
    txt_path = r'C:\Users\PC\Desktop\temporarily\practise\lingq\media\documents\test@example.com\test0txt'
    list_ref, list_id = get_lists_txt(txt_path)
    
    with open('check_text_file', 'w', encoding='utf-8') as file:
        json.dump(list_id, file,  indent=4)