import importlib
import json
import os
from PyQt6.QtWidgets import QLabel

# Settings persistence moved here (was in settings.py)
_settings_path = os.path.join(os.path.dirname(__file__), 'Data', 'settings.json')

def _settings_read():
    try:
        with open(_settings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _settings_write(data):
    try:
        with open(_settings_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def get_language(default='de'):
    d = _settings_read()
    return d.get('language', default)


def get_settings_default_language():
    """Return the configured default language from settings.json if present."""
    d = _settings_read()
    return d.get('default_language')


def get_available_languages():
    """Derive available language codes from names.json.

    Order preference:
    1. Codes from `window_title` (preserve order)
    2. Codes found in other top-level dicts
    3. Ensure settings default (if set) is first
    Returns a list of language codes (non-empty).
    """
    names_path = os.path.join(os.path.dirname(__file__), 'Data', 'names.json')
    try:
        with open(names_path, 'r', encoding='utf-8') as f:
            names = json.load(f)
    except Exception:
        names = {}

    codes = []
    wt = names.get('window_title')
    if isinstance(wt, dict):
        for k in wt.keys():
            if k not in codes:
                codes.append(k)

    # Collect codes from other top-level dicts that actually look like language maps.
    # Skip grouped structures like `menu_punkte` whose keys are label identifiers.
    def _looks_like_lang_map(d):
        if not isinstance(d, dict) or not d:
            return False
        # language maps map short language codes to strings, e.g. { 'de': 'Text', 'en': 'Text' }
        # Accept keys of length 2 or 3 and string values.
        for k, v in d.items():
            if not (isinstance(k, str) and 1 <= len(k) <= 3):
                return False
            if not isinstance(v, str):
                return False
        return True

    for key, val in names.items():
        if key == 'window_title':
            continue
        if isinstance(val, dict) and _looks_like_lang_map(val):
            for k in val.keys():
                if k not in codes:
                    codes.append(k)

    # Ensure settings default language is first if present
    settings_default = get_settings_default_language()
    if settings_default and settings_default in codes:
        codes = [settings_default] + [c for c in codes if c != settings_default]

    if not codes:
        codes = ['de']
    return codes

def set_language(lang_code):
    d = _settings_read()
    d['language'] = lang_code
    _settings_write(d)

def clear_content(content_layout):
    while content_layout.count():
        item = content_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()


def update_content(idx, content_layout, *args, **kwargs):
    """
    Backwards-compatible loader for UI modules.

    Accepts legacy signature with extra positional args (translation, settings_path,
    button_refs, button5) as well as the simplified signature used now.
    """
    # Normalize parameters for backward compatibility
    # possible legacy args order: (translation, settings_path, button_refs, button5)
    settings_path = kwargs.get('settings_path', None)
    button_refs = kwargs.get('button_refs', None)
    button5 = kwargs.get('button5', None)
    if len(args) >= 1 and settings_path is None:
        # args[0] might be translation in legacy calls; shift accordingly
        if len(args) >= 2:
            settings_path = args[1]
        if len(args) >= 3:
            button_refs = args[2]
        if len(args) >= 4:
            button5 = args[3]

    clear_content(content_layout)
    # Mapping Button-Index to module names (module name relative to package)
    module_map = {
        0: 'package_one.extensions.einstellung.ui_einstellung',
        1: 'package_one.extensions.modbus_template_konfigurator.ui_modbus_template',
    }
    module_name = module_map.get(idx)
    if module_name:
        # Try importing the module; be resilient to different package contexts.
        ui_module = None
        try:
            ui_module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            # Try common alternative prefixes
            prefixes = []
            if __package__:
                prefixes.append(__package__ + '.')
            prefixes.extend(['src.package_one.', 'package_one.'])
            print(f"import {module_name!r} failed; trying prefixes={prefixes}")
            for p in prefixes:
                try:
                    ui_module = importlib.import_module(p + module_name)
                    break
                except Exception:
                    continue
            if ui_module is None:
                # re-raise original error to preserve traceback
                raise
        # extract top_widgets if provided and pass through to ui module
        top_widgets = kwargs.get('top_widgets', None)
        # Call widget factory without translation/callback
        try:
            if top_widgets is not None:
                widget = ui_module.get_widget(None, top_widgets=top_widgets)
            else:
                widget = ui_module.get_widget(None)
        except TypeError:
            if top_widgets is not None:
                widget = ui_module.get_widget(top_widgets=top_widgets)
            else:
                widget = ui_module.get_widget()
        content_layout.addWidget(widget)
    else:
        label = QLabel('Kein UI-Modul gefunden!')
        content_layout.addWidget(label)
