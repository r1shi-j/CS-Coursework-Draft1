import tkinter as tk
from tkinter import messagebox
import traceback
import sys
from app import App
# usual tkinter imports
# importing traceback and sys for error handling
# importing our actual App class to run it

# MARK: Error Handler
# function to show error message in popup window
def show_error_message(exc_type, exc_value, exc_traceback):
    # getting the error
    error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    # printing the error
    print(error_details, file=sys.stderr)
    # if error is not during main view/app load
    if "root" not in globals() or not root.winfo_exists():
        # creating new window and showing error message
        temp_root = tk.Tk()
        temp_root.withdraw()
        messagebox.showerror("Critical Error", f"An error occurred:\n\n{error_details}", parent=temp_root)
        temp_root.destroy()
    else:
        # showing error message
        messagebox.showerror("Critical Error", f"An error occurred:\n\n{error_details}")

# MARK: Main
# creating and running the app, attatching error handlers
if __name__ == "__main__":
    sys.excepthook = show_error_message
    root = tk.Tk()
    root.report_callback_exception = show_error_message
    app = App(root)
    app.mainloop()

# TODO
# split long lines up

# FIXME
# Tournament type doesn't currently do anything: temporary solution is to disable creation
# Adding/removing players from a tournament will disrupt brackets: temporary solution is locking players by disabling adding and removing players from a tournament
# Only 16 player single elimination is supported: temporary solution is requiring 16 players, by validation, in future maybe a restriction of at least 4 players