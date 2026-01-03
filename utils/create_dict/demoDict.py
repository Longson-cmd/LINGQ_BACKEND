import spacy                      # Import spaCy: NLP library for tokenization, POS tagging, lemmatization
from word2word import Word2word   # Import Word2word: bilingual dictionary lookup (offline)
import time                       # Import time module (not used here, but often for profiling)

# load once at startup
nlp = spacy.load("en_core_web_sm") # Load the English spaCy model (small, fast, CPU-friendly)
en2vi = Word2word("en", "vi")      # Initialize English → Vietnamese dictionary

def lookup_word(word: str):
    # Run the NLP pipeline on the input word
    doc = nlp(word)

    # Get the first token (safe here because input is expected to be a single word)
    token = doc[0]

    # Prepare the output structure
    result = {
        "surface": word,                  # Original word as provided by the user
        "lemma": token.lemma_.lower(),     # Base form of the word (run → run, running → run)
        "pos": token.pos_,                # Part of speech (NOUN, VERB, ADJ, ADV, etc.)
        "meanings": []                    # Placeholder for Vietnamese meanings
    }

    # Try direct dictionary lookup first (fastest and most accurate for exact matches)
    meanings = en2vi(word.lower())

    # If no result found, try looking up the lemma instead
    if not meanings:
        meanings = en2vi(result["lemma"])

    # Normalize meanings:
    # - remove duplicates using a set
    # - replace "_" with spaces (e.g. "thức_dậy" → "thức dậy")
    # - convert to lowercase for consistency
    # - sort for stable output
    result["meanings"] = sorted({
        m.replace("_", " ").lower()
        for m in meanings
    })

    # Return the final structured result
    return result


words = [
    "running", "ran", "thing", "king", "passed", "news",
    "goes", "better", "working", "studies"
] 

start = time.perf_counter()

for word in words:
    print(lookup_word(word))

results = [lookup_word(w) for w in words]

end = time.perf_counter()

print(f"Processed {len(words)} words")
print(f"Total time: {(end - start) * 1000:.2f} ms")
print(f"Avg per word: {(end - start) * 1000 / len(words):.3f} ms")
