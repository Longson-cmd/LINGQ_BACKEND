import json
import os
from utils.paths import PROJECT_DIR

# DICT_PATH = BASE_DIR / "dictionary_app" / "data" / "Dictionary.json"

DICT_PATH = os.path.join(PROJECT_DIR,'core' ,'data', 'Dictionary.json')
print(DICT_PATH)
print(os.path.exists(DICT_PATH))
with open(DICT_PATH, 'r', encoding='utf-8') as file:
    DICTIONARY = json.load(file)
    

