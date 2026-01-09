import importlib
import json
import os
from PyQt6.QtWidgets import QLabel

# Settings persistence moved here (was in settings.py)
_settings_path = os.path.join(os.path.dirname(__file__), 'settings.json')

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
    # Mapping Button-Index to module names
    module_map = {
        0: 'extensions.einstellung.ui_einstellung',
    }
    module_name = module_map.get(idx)
    if module_name:
        ui_module = importlib.import_module(module_name)
        # Call widget factory without translation/callback
        try:
            widget = ui_module.get_widget(None)
        except TypeError:
            widget = ui_module.get_widget()
        content_layout.addWidget(widget)
    else:
        label = QLabel('Kein UI-Modul gefunden!')
        content_layout.addWidget(label)
