import tkinter as tk
from app import App

# creating and running the app
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.mainloop()

### Bugs
# Tournament type doesn't currently do anything: temporary solution is leave it as it is
# Adding/removing players from a tournament will disrupt brackets: temporary solution is locking players
# Only 16 player single elimination is supported: temporary solution is requiring 16 players, in future maybe a restriction of at least 4 players
#* hints not showing
#* rivalry statistics not working properly

### Redo UI
# choosing tournament type (create and edit tournament)
# creating tournament type (create and edit tournament)
# brackets view

# Sorting/searching algorithms
# Validation
# 2D Array
# Recursion
# Commenting

# block window resizing
# bind escape key to deactivate search field
# bind cmd backspace to clear field - update for windows use control instead?
# add animations or subtle color change on hover for buttons/labels
# add cursor styling, underline, color change on hover
# using "" instead of '' for strings
# use (,) instead of [] in sql
# all functions have return and type hints