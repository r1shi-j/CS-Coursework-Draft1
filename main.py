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
# Statistics view

### Bugs
# Adding/removing players from a tournament will disrupt brackets
# Solution is to lock current players, but can add new players
# Tournament type doesnt currently do anything
# Must have 16 players in a tournament otherwise bracket creating will fail
# Tournament overview doesnt show the current round or players still in/out

### After prototype
# Create account view
# Login view
# Add styling everywhere
# Add validation to forms everywhere
# Make ui better, sizing, padding, spacing ect