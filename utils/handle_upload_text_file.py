import os 
from ebooklib import epub
from bs4 import BeautifulSoup
from pdfminer.high_level import extract_text
from docx import Document
import chardet
import io
from core.models import Words, Phrases
from utils.extract_data import get_lists_txt, clean_word


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

    words_qs = Words.objects.filter(user = request.user)
    status_word_dict = {w.word_key : w.word_status for w in words_qs}
    phrases_qs = Phrases.objects.filter(user = request.user)
    phrase_lists = [(ph.phrase.split() , ph.phrase_status) for ph in phrases_qs]
   
    for item in list_id:
        list_words_in_lesson.append({
            "word" : item[0],
            "status" : status_word_dict.get(clean_word(item[0]), 6),
            "p_idx" : item[1][0],
            "s_idx" : item[1][1],
            "phrase_status" : 0
        })

    group_by_sentence = group_by_para_or_sentence(list_words_in_lesson, "s_idx")
    for items_in_sentence in group_by_sentence:
        sentence_list = [clean_word(item.get("word")) for item in items_in_sentence]
        for phrase_list, phrase_status in phrase_lists:
            if len(sentence_list) < len(phrase_list):
                continue
            for i in range(len(sentence_list) - len(phrase_list) + 1):
                if sentence_list[i: i+len(phrase_list)] == phrase_list:
                    for j in range(len(phrase_list)):
                        items_in_sentence[i+j]["phrase_status"] = phrase_status

    list_words_in_lesson = []

    for items_in_sentence in group_by_sentence:
        list_words_in_lesson.extend(items_in_sentence)

    group_by_para = group_by_para_or_sentence(list_words_in_lesson, "p_idx")
    group_by_para_sentence = [group_by_para_or_sentence(item, "s_idx") for item in group_by_para]

    return group_by_para_sentence

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


