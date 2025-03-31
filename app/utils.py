# app/utils.py
def sanitize_filename(name):
    return name.lower().replace("++", "pp").replace("#", "sharp").replace(" ", "_")
