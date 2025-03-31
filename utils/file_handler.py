import json
import logging

def load_data(filepath):
    """Lädt Daten aus einer JSON-Datei und gibt sie als Liste zurück."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Datei nicht gefunden: {filepath}")
        return []
    except json.JSONDecodeError:
        logging.error(f"Fehler beim Parsen der Datei: {filepath}")
        return []
    except Exception as e:
        logging.exception(f"Unbekannter Fehler beim Laden von {filepath}")
        return []

def save_data(filepath, data):
    """Speichert eine Liste als JSON-Datei."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.exception(f"Fehler beim Speichern in {filepath}")
