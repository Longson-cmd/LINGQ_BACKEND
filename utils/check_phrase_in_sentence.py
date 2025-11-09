

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

sentence = input().split
phrase = input().split()

def check_phrase_in_sentence():
    if not phrase[0] in sentence:
        return False
    else:
        pass

def issublist(main_list, sub_list):
    if len(sub_list) > len(main_list):
        return False
    for i in range(len(main_list) - len(sub_list) +1):
        if main_list[i: i+len(sub_list)] == sub_list:
            return True
    return False