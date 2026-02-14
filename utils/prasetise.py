from lemminflect import getAllInflections

# print(getAllInflections("run", upos="VERB"))
# print(getAllInflections("dog", upos="NOUN"))
# print(getAllInflections("big", upos="ADJ"))

from word2word import Word2word

en2vi = Word2word("en", "vi")

def exists_in_word2word(word: str) -> bool:
    try:
        result = en2vi(word)
        return bool(result)
    except KeyError:
        return False


exists_in_word2word("quickly")   # True (usually)
exists_in_word2word("fastly")    # False
exists_in_word2word("hardly")    # True
exists_in_word2word("friendlyly")# False
