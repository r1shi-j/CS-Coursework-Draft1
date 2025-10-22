import tkinter as tk
from app import App

# creating and running the app
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.mainloop()

### FIXME Bugs
# window title doesnt change based on navigation view
# Add column headers to tournament home menu
# at end of tournament, calculate and set all player tournament result
# Entering data must be done to the correct data type
# Adding/removing players from a tournament will disrupt brackets
# Solution is to lock current players, but can add new players
# Tournament type doesnt currently do anything
# Only 16 player single elimination is supported
# Look at all to-dos

### TODO After prototype
# Statistics view
# Create account view
# Login view
# Add styling everywhere
# cursor styling using `, cursor="plus"`
# Add validation to forms everywhere
# Make ui better, sizing, padding, spacing ect