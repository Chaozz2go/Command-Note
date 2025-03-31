# main.py

import sys
import traceback
from app.gui import CommandManagerApp

def main():
    try:
        app = CommandManagerApp()
        app.mainloop()
    except Exception as e:
        # Optional: Fehler-Logging in Datei
        with open("crash.log", "w", encoding="utf-8") as f:
            traceback.print_exc(file=f)
        print("Ein unerwarteter Fehler ist aufgetreten. Details stehen in 'crash.log'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
