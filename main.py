# import locale
import tkinter as tk
from app import App

if __name__ == "__main__":
    # locale.setlocale(locale.LC_TIME, 'en_GB')
    root = tk.Tk()
    app = App(root)
    app.mainloop()

### Forms to do
# Tournament Bracket viewer
# Tournament overview data
# Input race results
# Input grand prix results
# Statistics view

### After prototype
# Create account view
# Login view
# Block all closing window via window close button (traffic lights ect, check on windows)
# Add styling everywhere
# Add validation to forms everywhere
# Make ui better, sizing, padding, spacing ect