from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
import os
import json
from . import logic_einstellung
from PyQt6.QtWidgets import QApplication
from typing import cast
from PyQt6.QtCore import QObject, Qt
from package_one.main import get_language, get_settings_default_language, get_available_languages


def _read_names():
    path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'names.json'))
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _write_names(data):
    path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'Data', 'names.json'))
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


def get_widget(translation=None, *args, **kwargs):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    # align all UI elements to the top of the settings widget
    try:
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    except Exception:
        # fallback for older Qt bindings
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    title_lbl = QLabel(logic_einstellung.get_text())
    layout.addWidget(title_lbl)

    names = _read_names()
    # derive available languages from names.json (fallback to common set)
    try:
        lang_order = get_available_languages()
    except Exception:
        lang_order = names.get('language_order', ['de', 'en', 'ru'])
    # prefer default from settings.json, otherwise use first derived language
    settings_default = get_settings_default_language()
    default_name = settings_default or (lang_order[0] if lang_order else 'de')

    combo = QComboBox()
    label_map = {'de': 'Deutsch', 'en': 'English', 'ru': 'Русский'}
    for code in lang_order:
        combo.addItem(label_map.get(code, code), code)

    # determine currently selected language from persisted settings
    try:
        current = get_language(default=default_name)
    except Exception:
        current = default_name
    try:
        idx = lang_order.index(current)
    except Exception:
        idx = 0
    combo.setCurrentIndex(idx)

    # set prompt label text for settings page on initial load (if provided by caller)
    try:
        settings_group = names.get('settings_page', {})
        labels_root = names
        labels_group = names.get('labels', {})
        labels_menu = names.get('menu_punkte', {})
        v = settings_group.get('choose_prompt') or labels_root.get('choose_prompt') or labels_group.get('choose_prompt') or labels_menu.get('choose_prompt')
        if isinstance(v, dict):
            prompt_text = v.get(current) or next(iter(v.values()))
        else:
            prompt_text = v or 'choose_prompt'
        top_widgets = kwargs.get('top_widgets', {})
        prompt_widget = top_widgets.get('prompt_label')
        if prompt_widget is not None and hasattr(prompt_widget, 'setText'):
            try:
                prompt_widget.setText(prompt_text)
            except Exception:
                pass
    except Exception:
        pass

    def on_change(i):
        code = combo.itemData(i)
        # persist language in settings
            try:
                from package_one.main import set_language
                set_language(code)
            except Exception:
                pass
        # update main window titles and widgets
        try:
            n = _read_names()
            wt = n.get('window_title')
            if isinstance(wt, dict):
                new_title = wt.get(code) or next(iter(wt.values()))
            else:
                new_title = wt or 'Toolbox'
            # set title on all top-level windows (guard against QCoreApplication typing)
            app = cast(QApplication, QApplication.instance())
            if app and hasattr(app, 'topLevelWidgets'):
                for w in app.topLevelWidgets():
                    try:
                        w.setWindowTitle(new_title)
                    except Exception:
                        pass
            # update registered widgets (labels may be under settings_page, at root, under "labels", or under "menu_punkte")
            labels_settings = n.get('settings_page', {})
            labels_root = n
            labels_group = n.get('labels', {})
            labels_menu = n.get('menu_punkte', {})
            mapping = {
                'mainmenu_btn': 'menu_main',
                'modbus_btn': 'modbus_template',
                'settings_btn': 'settings',
                'prompt_label': 'choose_prompt'
            }
            # extensions now receive a `top_widgets` dict from the caller
            top_widgets = kwargs.get('top_widgets', {})
            for obj_name, lbl_key in mapping.items():
                widget = top_widgets.get(obj_name)
                if widget is None:
                    continue
                v = labels_settings.get(lbl_key) or labels_root.get(lbl_key)
                if v is None:
                    v = labels_group.get(lbl_key)
                if v is None:
                    v = labels_menu.get(lbl_key)
                if isinstance(v, dict):
                    text = v.get(code) or next(iter(v.values()))
                else:
                    text = v or lbl_key
                try:
                    if hasattr(widget, 'setText'):
                        widget.setText(text)
                except Exception:
                    continue
        except Exception:
            pass

    combo.currentIndexChanged.connect(on_change)
    layout.addWidget(combo)

    return widget
