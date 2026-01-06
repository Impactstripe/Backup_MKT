
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QPushButton, QHeaderView
import logic_button1

def get_widget(translation, *args, **kwargs):
    widget = QWidget()
    layout = QVBoxLayout(widget)

    # Toolbar
    toolbar_widget = QWidget()
    toolbar_layout = QHBoxLayout(toolbar_widget)
    btn_add = QPushButton(translation.t('add') if hasattr(translation, 't') else 'Hinzufügen')
    btn_remove = QPushButton(translation.t('remove') if hasattr(translation, 't') else 'Entfernen')
    btn_refresh = QPushButton(translation.t('refresh') if hasattr(translation, 't') else 'Aktualisieren')
    toolbar_layout.addWidget(btn_add)
    toolbar_layout.addWidget(btn_remove)
    toolbar_layout.addWidget(btn_refresh)
    toolbar_layout.addStretch()
    layout.addWidget(toolbar_widget)

    # Tabelle
    table = QTableWidget(3, 6)
    table.setHorizontalHeaderLabels([
        translation.t('col1') if hasattr(translation, 't') else 'Spalte 1',
        translation.t('col2') if hasattr(translation, 't') else 'Spalte 2',
        translation.t('col3') if hasattr(translation, 't') else 'Spalte 3',
        translation.t('col4') if hasattr(translation, 't') else 'Spalte 4',
        translation.t('col5') if hasattr(translation, 't') else 'Spalte 5',
        translation.t('col6') if hasattr(translation, 't') else 'Spalte 6',
    ])
    for row, row_data in enumerate([
        ['A', '1', 'X', 'Alpha', 'Rot', '100'],
        ['B', '2', 'Y', 'Beta', 'Blau', '200'],
        ['C', '3', 'Z', 'Gamma', 'Grün', '300']
    ]):
        for col, value in enumerate(row_data):
            table.setItem(row, col, QTableWidgetItem(value))
    table.setStyleSheet('color: black; background: white;')
    table.horizontalHeader().setStretchLastSection(True)
    for col in range(table.columnCount()):
        table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    btn_add.clicked.connect(lambda: logic_button1.add_row(table))
    btn_remove.clicked.connect(lambda: logic_button1.remove_row(table))

    return widget
