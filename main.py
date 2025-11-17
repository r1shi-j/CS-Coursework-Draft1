import tkinter as tk
from app import App

# creating and running the app
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.mainloop()

### FIXME Bugs
# at end of tournament, calculate and set all player tournament result

# Adding/removing players from a tournament will disrupt brackets
# Solution is to lock current players, but can add new players
# Tournament type doesnt currently do anything
# Only 16 player single elimination is supported

### Implement
# Statistics view
# Create account view
# Login view

### Redo UI
#* input race/gp results
# choosing tournament type (create and edit tournament)
# creating tournament type (create and edit tournament)
# brackets view

#* Add validation to forms everywhere
# add animations or subtle color change on hover for buttons/labels
# add cursor styling, underline, color change on hover
# block window resizing
# bind escape key to deactive search field