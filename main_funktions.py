import importlib
from PyQt6.QtWidgets import QLabel

def clear_content(content_layout):
    while content_layout.count():
        item = content_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()


def update_content(idx, content_layout, settings_path=None, button_refs=None, button5=None):
    """
    Load UI module by index and add its widget to the content layout.
    Language/translation support removed; signature keeps optional params
    for compatibility with existing callers.
    """
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
