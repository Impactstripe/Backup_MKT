from PyQt6.QtWidgets import QWidget, QPushButton
from typing import Optional

# Common UI helper elements for the mc_ui styles


class MCUIFactory:
    """Factory for creating common UI elements styled for the mc_ui theme."""

    def __init__(self):
        # optional UI context used for one-call menu button creation
        self.menu_button_layout = None
        self.content_layout = None
        self.settings_path = None
        self.button_refs = None
        self.button5 = None
        self.top_widgets = None
        self.label_getter = None

    def make_section_title(self, text: str) -> QWidget:
        from PyQt6.QtWidgets import QLabel
        w = QLabel(text)
        w.setObjectName('mc_section_title')
        return w

    def make_status_label(self, text: str) -> QWidget:
        from PyQt6.QtWidgets import QLabel
        w = QLabel(text)
        w.setObjectName('mc_status_label')
        return w

    def make_button(self, text: str, object_name: Optional[str] = None, fixed_width: Optional[int] = None) -> QPushButton:
        from PyQt6.QtWidgets import QPushButton, QSizePolicy
        b = QPushButton(text)
        if object_name:
            b.setObjectName(object_name)
        try:
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        except Exception:
            pass
        if fixed_width is not None:
            try:
                b.setFixedWidth(fixed_width)
            except Exception:
                pass
        return b

    def add_menu_button(self, text: str, callback, object_name: Optional[str] = None, fixed_width: Optional[int] = None) -> QPushButton:
        """Create a sidebar menu button and connect it to `callback`.

        The returned widget is a `QPushButton` with `clicked` connected to
        `callback`. `callback` can be a callable accepting no args or a
        callable accepting a single `checked` argument.
        """
        # Resolve label via label_getter if available (text may be a key)
        label = text
        if self.label_getter:
            try:
                label = self.label_getter(text)
            except Exception:
                label = text

        btn = self.make_button(label, object_name=object_name, fixed_width=fixed_width)

        # add to sidebar layout if provided
        try:
            if self.menu_button_layout is not None:
                self.menu_button_layout.addWidget(btn)
        except Exception:
            pass

        # track in button_refs if provided
        try:
            if isinstance(self.button_refs, list):
                self.button_refs.append(btn)
        except Exception:
            pass

        # normalize callback signature to accept the `checked` parameter
        try:
            btn.clicked.connect(lambda checked=False, cb=callback: cb() if cb is not None else None)
        except Exception:
            try:
                btn.clicked.connect(callback)
            except Exception:
                pass

        # register with main_funktions for legacy behavior when possible
        try:
            from .. import main_funktions
            # call registration if content/layout/context is present
            if self.content_layout is not None and self.settings_path is not None and self.button_refs is not None:
                try:
                    main_funktions.add_menu_button(btn, self.content_layout, self.settings_path, self.button_refs, self.button5, top_widgets=self.top_widgets)
                except Exception:
                    # ignore registration errors
                    pass
        except Exception:
            pass

        return btn

    def set_menu_context(self, button_layout=None, content_layout=None, settings_path=None, button_refs=None, button5=None, top_widgets=None, label_getter=None):
        """Provide context used by `add_menu_button` so main can call it with only name+callback.

        Example: `ui_factory.set_menu_context(button_layout, content_layout, settings_path, button_refs, button5, top_widgets, _lbl)`
        """
        self.menu_button_layout = button_layout
        self.content_layout = content_layout
        self.settings_path = settings_path
        self.button_refs = button_refs
        self.button5 = button5
        self.top_widgets = top_widgets
        self.label_getter = label_getter


# Backwards-compatible helpers
def make_section_title(text: str) -> QWidget:
    return MCUIFactory().make_section_title(text)


def make_status_label(text: str) -> QWidget:
    return MCUIFactory().make_status_label(text)


def make_button(text: str, object_name: Optional[str] = None, fixed_width: Optional[int] = None) -> QPushButton:
    return MCUIFactory().make_button(text, object_name=object_name, fixed_width=fixed_width)


def add_menu_button(text: str, callback, object_name: Optional[str] = None, fixed_width: Optional[int] = None) -> QPushButton:
    return MCUIFactory().add_menu_button(text, callback, object_name=object_name, fixed_width=fixed_width)
