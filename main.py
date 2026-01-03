import tkinter as tk
from tkinter import messagebox
import traceback
import sys
import argparse
from app import App
# usual tkinter imports
# importing traceback and sys for error handling
# argparse for command line parsing
# importing our actual App class to run it

# constant for the default database to open when none provided
DEFAULT_DATABASE = "test_database.db"

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
if __name__ == "__main__":
    # adding command line parser when run, to catch flags
    parser = argparse.ArgumentParser(description=f"Mario Kart Tournament App: running without any arguments opens the existing {DEFAULT_DATABASE} database")
    parser.add_argument("mode", choices=["new", "run"], nargs="?", default="run", help="Mode: 'new' to create a new database, 'run' to use an existing database")
    parser.add_argument("db_name", nargs="?", default=DEFAULT_DATABASE, help="Name of the database file to use")
    args = parser.parse_args()
    is_new = True if args.mode == "new" else False
    # printing mode
    print(f"--- Starting in {args.mode.upper()} mode using database: {args.db_name}, is new database: {is_new} ---")
    sys.excepthook = show_error_message
    root = tk.Tk()
    root.report_callback_exception = show_error_message
    # launching app with database config
    app = App(root, (args.db_name, is_new))
    app.mainloop()

# TODO
# split long lines up
# remove TODO, FIXME, #* for temporary code

# FIXME
# Tournament type doesn't currently do anything: temporary solution is to disable creation
# Adding/removing players from a tournament will disrupt brackets: temporary solution is locking players by disabling adding and removing players from a tournament
# Only 16 player single elimination is supported: temporary solution is requiring 16 players, by validation, in future maybe a restriction of at least 4 players