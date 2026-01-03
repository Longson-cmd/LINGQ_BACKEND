import os 
from ebooklib import epub
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from docx import Document
import chardet
import io
from core.models import Words, Phrases, Word_Tags, Word_Meanings, Phrase_Meanings, Phrase_Tags
from utils.extract_data import get_lists_txt, clean_word
import json
from utils.paths import BASE_DIR
import os

print('BASE_DIR', BASE_DIR)
dict_path = os.path.join(BASE_DIR, 'Dictionary.json')
with open(dict_path, 'r', encoding='utf-8') as file:
    Dict_data = json.load(file)

# ============================================================
# 1. Group words by paragraph index or sentence index
# ============================================================

def group_by_para_or_sentence(timestamp_word_level, group_type):
    """
    Group words by paragraph ('p_idx') or sentence ('s_idx') index.

    Args:
        timestamp_word_level (list): list of word objects with indexes
        group_type (str): key to group by ('p_idx' or 's_idx')

    Returns:
        list[list]: nested list of grouped words
    """
    words_in_the_same_type = []
    current_object = []
    current_idx = 0

    for word in timestamp_word_level:
        # Continue same group if index matches
        if word[group_type] == current_idx:
            current_object.append(word)
        else:
            # Start a new group
            words_in_the_same_type.append(current_object)
            current_idx = word[group_type]
            current_object = [word]

    if current_object:
        words_in_the_same_type.append(current_object)

    return words_in_the_same_type

# def check_phrase_in_sentence(list_sentence, list_phrase):


def create_lesson(request, txt_path):
    list_ref, list_id = get_lists_txt(txt_path)
    list_words_in_lesson = []
    list_phrases_in_text = []

    words_qs = Words.objects.filter(user = request.user)
    status_word_dict = {w.word_key : w.word_status for w in words_qs}
    phrases_qs = Phrases.objects.filter(user = request.user)
    phrase_lists = [(ph.phrase.split() , ph.phrase_status) for ph in phrases_qs]
   
    for  word_idx, item in enumerate(list_id):
        list_words_in_lesson.append({
            "word" : item[0],
            "status" : status_word_dict.get(clean_word(item[0]), 6),
            'w_idx' : word_idx,
            "p_idx" : item[1][0],
            "s_idx" : item[1][1],
            "idx_w_in_s": item[1][2],
            "type" : 'word',
            "visible_in_phrase": True
        })

    group_by_sentence = group_by_para_or_sentence(list_words_in_lesson, "s_idx")
    
    list_sentences = []
    for items in group_by_sentence:
        list_words = [w['word'] for w in items]
        sentence = ' '.join(list_words)
        list_sentences.append(sentence)

    for items_in_sentence in group_by_sentence:
        sentence_list = [clean_word(item.get("word")) for item in items_in_sentence]
        for phrase_list, phrase_status in phrase_lists:
            if len(sentence_list) < len(phrase_list):
                continue
            i = 0
            while i < (len(sentence_list) - len(phrase_list) + 1):
                if sentence_list[i: i+len(phrase_list)] == phrase_list:

                    list_phrases_in_text.append((' '.join(phrase_list), phrase_status))
                    chuck = items_in_sentence[i : i + len(phrase_list)]
                    items_in_sentence[i] = {
                        "phrase" : chuck,
                        "status" : phrase_status,
                        "p_idx" : items_in_sentence[i]['p_idx'],
                        "s_idx" : items_in_sentence[i]['s_idx'],
                        "type" : 'phrase',
                        'visible': True
                    }

                    del items_in_sentence[i + 1: i + len(phrase_list)]
                    del sentence_list[i+ 1: i + len(phrase_list)]
                    i += len(phrase_list)
                else:
                    i += 1

                  

    list_words_in_lesson = []

    for items_in_sentence in group_by_sentence:
        list_words_in_lesson.extend(items_in_sentence)


    group_by_para = group_by_para_or_sentence(list_words_in_lesson, "p_idx")

    Tags_Meanings = {}

    for item in list_ref:
        word = Words.objects.filter(word_key = item, user = request.user).first()
        item_data_in_dict = Dict_data.get(item, {
            "global_tags": [],
            "global_meanings" : []
        })
        global_tags = item_data_in_dict["global_tags"]
        global_meanings = item_data_in_dict["global_meanings"]

  
        if not word:
            tags = []
            meanings = []
            
        else:
            meanings = list(word.word_meanings_set.values_list('meaning', flat= True))
            tags = list(word.word_tags_set.values_list('tag', flat = True))
        Tags_Meanings[item] = {
            'tags': tags,
            'your_meanings': meanings,
            'global_tags': global_tags,
            'global_meanings': global_meanings,
            'status': status_word_dict.get(item, 6)
        }
    for phrase_in_text, phrase_status in list_phrases_in_text:
        phrase = Phrases.objects.get(user = request.user, phrase = phrase_in_text)
        tags = list(phrase.phrase_tags_set.values_list('tag', flat = True))
        meanings = list(phrase.phrase_meanings_set.values_list('meaning', flat = True))
        # others_meanings = list(
        #     Phrase_Meanings.objects
        #     .filter(phrase__phrase = phrase_in_text)
        #     .exclude(phrase__user = request.user)
        #     .values_list('meaning', flat=True)
        #     .distinct()
        # )
        Tags_Meanings[phrase_in_text] = {
            'tags' : tags,
            'your_meanings': meanings,
            'status': phrase_status
        }


    return group_by_para, list_sentences, Tags_Meanings

# ---------- EPUB ----------     
def convert_epub_to_txt(uploaded_file):
    uploaded_file.seek(0)

    book = epub.read_epub(io.BytesIO(uploaded_file.read()))
    texts = []
    for item in book.get_items():
        if item.get_type() == 9:
            soup = BeautifulSoup(item.get_body_content(), 'lxml')
            texts.append(soup.get_text())
    return "\n".join(texts)

# ---------- PDF ----------\
def convert_pdf_to_txt(uploaded_file):
    uploaded_file.seek(0)
    text = extract_text(io.BytesIO(uploaded_file.read()))
    return text

# ---------- DOCX ----------
def convert_docx_to_txt(uploaded_file):
    uploaded_file.seek(0)
    doc  = Document(io.BytesIO(uploaded_file.read()))
    return "\n".join([p.text for p in doc.paragraphs])

# ---------- TXT ----------
def convert_txt_to_txt(uploaded_file):
    uploaded_file.seek(0)  
    raw_data = uploaded_file.read()
    encoding = chardet.detect(raw_data)["encoding"] or "utf-8"
    return raw_data.decode(encoding, errors="ignore")

def convert_input_to_txt(uploaded_file):
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".epub":
        content = convert_epub_to_txt(uploaded_file)
    elif ext == ".pdf":
        content = convert_pdf_to_txt(uploaded_file)
    elif ext == ".docx":
        content = convert_docx_to_txt(uploaded_file)
    elif ext == ".txt":
        content = convert_txt_to_txt(uploaded_file)
    else:
        raise ValueError(f"[⚠] Unsupported format: {ext}")
    print(f"[✔] Converted {ext} file → txt")
    return content




