import importlib

class TranslationManager:
    def __init__(self, default_lang='de'):
        self.current_lang = default_lang
        self.translations = self._load_translations(default_lang)

    def _load_translations(self, lang_code):
        lang_module = importlib.import_module(f'lang.{lang_code}')
        return lang_module.translations

    def set_language(self, lang_code):
        self.current_lang = lang_code
        self.translations = self._load_translations(lang_code)

    def t(self, key):
        return self.translations.get(key, key)
