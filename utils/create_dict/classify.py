# import nltk
# nltk.download("wordnet")


from nltk.corpus import wordnet as wn
from collections import defaultdict
import json

pos_map = defaultdict(set)

for syn in wn.all_synsets():
    for lemma in syn.lemma_names():
        pos_map[lemma.lower()].add(syn.pos())

# save lightweight POS-only map
with open("word_pos_map.json", "w", encoding="utf-8") as f:
    json.dump(
        {k: sorted(v) for k, v in pos_map.items()},
        f,
        ensure_ascii=False
    )

print("Saved", len(pos_map), "lemmas")














# import spacy
# from word2word import Word2word


POS_TAGS = [
    "ADJ",     # adjective
    "ADP",     # adposition (prepositions)
    "ADV",     # adverb
 
    "NOUN",    # noun

    "PRON",    # pronoun

    "VERB",    # main verb
]


# nlp = spacy.load('en_core_web_sm')

# en2vi = Word2word('en', 'vi')

list_verbs = []
list_abverbs = []
list_adjectives = []
list_nouns = []
list_prepositions = []
list_pronouns = []



