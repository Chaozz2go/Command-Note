import os
from utils import file_handler
from app.utils import sanitize_filename


class CategoryManager:
    """Verwaltet alle Dateioperationen rund um Kategorien und Befehle."""

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

    @staticmethod
    def get_all_categories():
        """Gibt eine Liste aller Kategorienamen (aus .json-Dateien) zurück."""
        categories = []
        if os.path.exists(CategoryManager.data_dir):
            for filename in os.listdir(CategoryManager.data_dir):
                if filename.endswith(".json"):
                    cat_name = os.path.splitext(filename)[0]
                    if cat_name.lower() == "win_shortcuts":
                        cat_name = "Windows-Shortcuts"
                    else:
                        cat_name = cat_name.capitalize()
                    categories.append(cat_name)
        return categories

    @staticmethod
    def get_category_file(category_name):
        """Gibt den vollständigen Pfad zur Datei der Kategorie zurück."""
        safe_name = sanitize_filename(category_name)
        return os.path.join(CategoryManager.data_dir, f"{safe_name}.json")

    @staticmethod
    def load_commands(category_name):
        """Lädt alle Befehle einer Kategorie."""
        path = CategoryManager.get_category_file(category_name)
        return file_handler.load_data(path)

    @staticmethod
    def save_commands(category_name, commands):
        """Speichert die Befehle einer Kategorie."""
        path = CategoryManager.get_category_file(category_name)
        file_handler.save_data(path, commands)

    @staticmethod
    def delete_category(category_name):
        """Löscht die Datei der Kategorie."""
        path = CategoryManager.get_category_file(category_name)
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def rename_category(old_name, new_name):
        """Benennt eine bestehende Kategorie um."""
        old_path = CategoryManager.get_category_file(old_name)
        new_path = CategoryManager.get_category_file(new_name)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
