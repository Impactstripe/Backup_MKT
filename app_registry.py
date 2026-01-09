"""Simple registry for top-level widgets so extensions can update them."""
WIDGETS = {}

def register_widget(name, widget):
    WIDGETS[name] = widget

def get_widget(name):
    return WIDGETS.get(name)
