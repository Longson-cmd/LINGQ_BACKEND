
import json
# from utils.extract_data import get_lists_from_text

import json
import re
import unicodedata



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
   

text_file_path = r"C:\Users\PC\Desktop\practise\lingq\test\test0.txt"
with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()
list_ref, list_id = get_lists_from_text(text)
json_data = {"list_ref": list_ref, "list_id" : list_id}


with open("check_json_text.json", 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)