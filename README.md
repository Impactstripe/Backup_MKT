# PyQt6 Beispielanwendung

Dieses Projekt ist eine modulare PyQt6-Anwendung mit:
- Flickable-Bereich mit Buttons
- Dynamischem Hauptinhalt
- Einstellungsmenü mit Sprachwahl (Deutsch/Englisch)
- Übersetzungen in separaten Sprachdateien
- Persistenter Speicherung der Spracheinstellung

## Starten

1. Python venv aktivieren:
   ```
   source .venv/bin/activate
   ```
2. Abhängigkeiten installieren:
   ```
   pip install PyQt6
   ```
3. Anwendung starten:
   ```
   python main.py
   ```

## Struktur
- `main.py` – Hauptlogik und UI-Management
- `ui_buttonX.py` – UI für jeden Button
- `logic_buttonX.py` – Logik für jeden Button
- `ui_settings.py` – Einstellungsmenü
- `lang/` – Sprachdateien (de.py, en.py)
- `translation_manager.py` – Globale Übersetzungsverwaltung
- `settings.json` – Speichert die gewählte Sprache

## Sprache ändern
Im Einstellungsmenü kann die Sprache für das gesamte Programm geändert werden.

## Lizenz
MIT