import tkinter as tk
from tkinter import messagebox
import traceback
import sys
from app import App

# function to show error message in popup window
def show_error_message(exc_type, exc_value, exc_traceback):
    # getting the error
    error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    # printing the error
    print(error_details, file=sys.stderr)
    # if error is not during main view/app load
    if 'root' not in globals() or not root.winfo_exists():
        # creating new window and showing error message
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror("Critical Error", f"An error occurred:\n\n{error_details}", master=temp_root)
        temp_root.destroy()
    else:
        # showing error message
        messagebox.showerror("Critical Error", f"An error occurred:\n\n{error_details}")

# creating and running the app, attatching error handlers
if __name__ == "__main__":
    sys.excepthook = show_error_message
    root = tk.Tk()
    root.report_callback_exception = show_error_message
    app = App(root)
    app.mainloop()

# # user feedback: messagebox.showinfo("title", "message")
# # more appropriate commenting
# # more suitable variable names
# # add animations or subtle color change on hover for buttons/labels
# # add cursor styling, underline, color change on hover

# # Sorting/searching algorithms
# # Validation (add other validation for range check and lookup check)
# # 2D Array
# # Recursion
# # Commenting
# add try-catching input/validation/divide0/readwrite

# prefill with 1 tournament type, all circuits and demo players and tournaments


# MARK: Bugs
# Tournament type doesn't currently do anything: temporary solution is leave it as it is
# Adding/removing players from a tournament will disrupt brackets: temporary solution is locking players
# Only 16 player single elimination is supported: temporary solution is requiring 16 players, in future maybe a restriction of at least 4 players

# MARK: Conventions
# block window resizing
# bind escape key to deactivate search field
# bind cmd backspace to clear field - update for windows use control instead?
# using "" instead of '' for strings
# use (,) instead of [] in sql
# all functions have return and type hints