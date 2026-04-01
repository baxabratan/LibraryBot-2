import json
import os

LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locales')

def load_locales():
    locales = {}
    if not os.path.exists(LOCALES_DIR):
        return locales
    for filename in os.listdir(LOCALES_DIR):
        if filename.endswith('.json'):
            lang_code = filename.split('.')[0]
            with open(os.path.join(LOCALES_DIR, filename), 'r', encoding='utf-8') as f:
                locales[lang_code] = json.load(f)
    return locales

LOCALES = load_locales()

def get_text(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in ['en', 'ru', 'uz', 'kaa'] else 'en'
    locales = LOCALES.get(lang, LOCALES.get('en', {}))
    text = locales.get(key, f"Missing key: {key}")
    if kwargs:
        text = text.format(**kwargs)
    return text
