# import locale
import tkinter as tk
from app import App

if __name__ == "__main__":
    # locale.setlocale(locale.LC_TIME, 'en_GB')
    root = tk.Tk()
    app = App(root)
    app.mainloop()