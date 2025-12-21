import tkinter as tk
from tkinter import ttk, messagebox
import re
from Utilities.animatedButton import AnimatedButton
from Utilities.FontStyling import Fonts as FS, Colours as FC
# importing relevant tkinter packages
# importing re for regex validation
# importing animatedButton to use custom coloured button
# importing FontStyling to use custom fonts and colours

class PlayersPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_view()

    def block_window_closure(self): return

    # building the players view homepage with buttons to create and edit players, search bar and list of players
    def build_view(self):
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack()
        
        # action buttons frame and buttons
        buttons_frame = ttk.Frame(self.form_frame)
        buttons_frame.pack(pady=(15, 8))

        capsule_frame = tk.Frame(buttons_frame, bg=FC.base)
        capsule_frame.pack()

        # the create button made from AnimatedButton with custom arguments
        # rounded corners are the left side only so that right side is flat to match with edit player
        self.create_btn = AnimatedButton(
            capsule_frame, text="Create Player", command=self.open_create_player,
            width=160, height=40, corner_radius=20, 
            base_colour=FC.base, hover_colour=FC.purple[1], font=FS.base2, 
            hover_cursor="crosshair", rounded_corners=["top_left", "bottom_left"]
        )
        self.create_btn.pack(side="left", padx=0)

        # the edit button made from AnimatedButton with custom arguments
        # rounded corners are the right side only so that left side is flat to match with create player
        AnimatedButton(
            capsule_frame, text="Edit Player", command=self.toggle_edit_mode,
            width=160, height=40, corner_radius=20,
            base_colour=FC.base, hover_colour=FC.gold[1], font=FS.base2,
            hover_cursor="spraycan", rounded_corners=["top_right", "bottom_right"]
        ).pack(side="left", padx=0)

        # both of these together make a large capsule shape like the create tournament button, but it is split in the middle into 2 different buttons

        # defining edit mode to be off
        self.edit_mode = False

        # creating the search bar frame
        search_frame = ttk.Frame(self.form_frame)
        search_frame.pack(pady=(7, 8))

        # subtitle, search field and clear button
        # binding keyboard buttons to clear and unfocus search field, with every key release triggering a search for real time searching
        # using subtitle style to get font size 12
        ttk.Label(search_frame, text="Search players:", style="Subtitle.TLabel").pack(side="left", padx=5)
        self.search_field = ttk.Entry(search_frame, width=20)
        self.search_field.pack(side="left", padx=5)
        self.search_field.bind("<KeyRelease>", self.search_players)
        self.search_field.bind(self.CLEAR_TEXT_FIELD, self.clear_entry)
        self.search_field.bind("<Escape>", lambda e: self.search_field.focus_set() or self.focus())
        # clear search button as a label so can add styling
        self.clear_search = ttk.Label(search_frame, text="⌫", width=2)
        self.clear_search.pack(side="left", padx=5)

        # binding hover and unhover to change the colour to red on hover
        def on_enter(): self.clear_search.config(foreground=FC.red[1])
        def on_leave(): self.clear_search.config(foreground=FC.black)
        # only calling the functions is edit_mode is off
        self.clear_search.bind("<Enter>", lambda e: on_enter() if not self.edit_mode else None)
        self.clear_search.bind("<Leave>", lambda e: on_leave() if not self.edit_mode else None)
        # binding clicking on the label to call remove search function
        self.clear_search.bind("<Button-1>", lambda e: self.remove_search() if not self.edit_mode else None)

        # creating the scroll container
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # the container for the search results
        self.results_frame = ttk.Frame(self.canvas)
        self.results_frame.pack()
        canvas_window = self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.results_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            self.canvas.itemconfig(canvas_window, width=event.width)
        self.canvas.bind("<Configure>", on_canvas_configure)

        # initially showing all players (no search query)
        self.show_results(self.controller.db.read_player_data())

    # opens the create player view
    def open_create_player(self):
        # creating a small pop up window for data entry
        # blocking action on other windows, and blocking window closure using red x
        win = tk.Toplevel(self)
        win.title("Create Player")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)
        # forcing the window to appear on top
        win.transient(self.controller) 
        win.lift()
        win.focus_force()

        # functions to clear the textfield when command backspace pressed
        def clear_fname(event=None):
            fname_entry.delete(0, tk.END)
        def clear_sname(event=None):
            sname_entry.delete(0, tk.END)
        def clear_age(event=None):
            age_entry.delete(0, tk.END)

        # text box for first name
        ttk.Label(win, text="First name:").grid(row=0, column=0, padx=10, pady=(16,8), sticky="e")
        fname_entry = ttk.Entry(win)
        fname_entry.grid(row=0, column=1, padx=(5,20), pady=(16,8))
        fname_entry.bind("<Escape>", lambda e: win.focus())
        fname_entry.bind(self.CLEAR_TEXT_FIELD, clear_fname)

        # text box for surname
        ttk.Label(win, text="Surname:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        sname_entry = ttk.Entry(win)
        sname_entry.grid(row=1, column=1, padx=(5,20), pady=8)
        sname_entry.bind("<Escape>", lambda e: win.focus())
        sname_entry.bind(self.CLEAR_TEXT_FIELD, clear_sname)

        # text box for age
        ttk.Label(win, text="Age:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        age_entry = ttk.Entry(win)
        age_entry.grid(row=2, column=1, padx=(5,20), pady=8)
        age_entry.bind("<Escape>", lambda e: win.focus())
        age_entry.bind(self.CLEAR_TEXT_FIELD, clear_age)

        # adding the player to the database, and then closing the window and refreshing the player view so that the new player is present
        def create_player():
            firstname = fname_entry.get()
            surname = sname_entry.get()
            age = age_entry.get()

            # presence check on all fields
            if firstname == "" or surname == "" or age == "":
                messagebox.showerror("Missing Info", "Please fill in all fields.")
                return
            # type check on age
            # trying to convert the text to an integer, if fails then show error
            try:
                age = int(age)
            except ValueError:
                messagebox.showerror("Invalid age", "Age must be a valid whole number.")
                return
            # range check on age
            if age < 5 or age > 100:
                messagebox.showerror("Bad data", "Please enter a reasonable age between 5 and 100")
                return
            # length check on names
            if len(firstname) < 2 or len(firstname) > 35:
                messagebox.showerror("Bad data", "Please enter a reasonable first name length between 2 and 35 characters")
                return
            if len(surname) < 2 or len(surname) > 35:
                messagebox.showerror("Bad data", "Please enter a reasonable surname length between 2 and 35 characters")
                return
            # type check on names to ensure only letters
            if re.fullmatch(r"[a-zA-Z ]*", firstname) is None:
                messagebox.showerror("Bad data", "Please enter a firstname using only letters")
                return
            if re.fullmatch(r"[a-zA-Z ]*", surname) is None:
                messagebox.showerror("Bad data", "Please enter a surname using only letters")
                return
            
            self.controller.db.create_player(firstname, surname, age)
            
            # showing message saying success
            messagebox.showinfo("title", "Player Created!")

            win.destroy()
            self.show_results(self.controller.db.read_player_data())

        # buttons to cancel or create
        # cancel closes this window, and create runs the above function
        AnimatedButton(
            win, text="Cancel", command=win.destroy,
            width=100, base_colour=FC.base, hover_colour=FC.cancel
        ).grid(row=3, column=0, padx=(20,0), pady=(10,15), sticky="w")

        AnimatedButton(
            win, text="Create", command=create_player, hover_cursor="mouse",
            width=100, base_colour=FC.green[0], hover_colour=FC.green[1]
        ).grid(row=3, column=1, padx=(0,20), pady=(10,15), sticky="e")
        
    # function to toggle edit mode
    # when going into edit mode, disable create button, search field and clear results button
    # when going out of edit mode, enable them again
    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.create_btn.set_state("disabled")
            self.search_field["state"] = "disabled"
            # self.clear_search: btn.config(foreground=FC.red[1])
            self.clear_search["state"] = "disabled"
        else:
            self.create_btn.set_state("normal")
            self.search_field["state"] = "normal"
            self.clear_search["state"] = "normal"

    # opens the edit player view
    def open_edit_player(self, player: tuple[str, str, str, int]):
        # creating a small pop up window for data entry
        # blocking action on other windows, and blocking window closure using red x
        win = tk.Toplevel(self)
        win.title("Edit Player")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)
        # forcing the window to appear on top
        win.transient(self.controller) 
        win.lift()
        win.focus_force()

        # functions to clear the textfield when command backspace pressed
        def clear_fname(event=None):
            fname_entry.delete(0, tk.END)
        def clear_sname(event=None):
            sname_entry.delete(0, tk.END)
        def clear_age(event=None):
            age_entry.delete(0, tk.END)

        # text box for first name, prefilling with the original data
        ttk.Label(win, text="First name:").grid(row=0, column=0, padx=(20,10), pady=(16,8), sticky="e")
        fname_entry = ttk.Entry(win)
        fname_entry.insert(0, player[1])
        fname_entry.grid(row=0, column=1, columnspan=2, padx=(5,20), pady=(16,8))
        fname_entry.bind("<Escape>", lambda e: win.focus())
        fname_entry.bind(self.CLEAR_TEXT_FIELD, clear_fname)

        # text box for surname, prefilling with the original data
        ttk.Label(win, text="Surname:").grid(row=1, column=0, padx=(15,10), pady=8, sticky="e")
        sname_entry = ttk.Entry(win)
        sname_entry.insert(0, player[2])
        sname_entry.grid(row=1, column=1, columnspan=2, padx=(5,20), pady=8)
        sname_entry.bind("<Escape>", lambda e: win.focus())
        sname_entry.bind(self.CLEAR_TEXT_FIELD, clear_sname)

        # text box for age, prefilling with the original data
        ttk.Label(win, text="Age:").grid(row=2, column=0, padx=(15,10), pady=8, sticky="e")
        age_entry = ttk.Entry(win)
        age_entry.insert(0, str(player[3]))
        age_entry.grid(row=2, column=1, columnspan=2, padx=(5,20), pady=8)
        age_entry.bind("<Escape>", lambda e: win.focus())
        age_entry.bind(self.CLEAR_TEXT_FIELD, clear_age)

        # function to update the data, and then go back
        def update_player():
            firstname = fname_entry.get()
            surname = sname_entry.get()
            age = age_entry.get()

            # presence check on all fields
            if firstname == "" or surname == "" or age == "":
                messagebox.showerror("Missing Info", "Please fill in all fields.")
                return
            # type check on age
            # trying to convert the text to an integer, if fails then show error
            try:
                age = int(age)
            except ValueError:
                messagebox.showerror("Invalid age", "Age must be a valid whole number.")
                return
            # range check on age
            if age < 5 or age > 100:
                messagebox.showerror("Bad data", "Please enter a reasonable age between 5 and 100")
                return
            # length check on names
            if len(firstname) < 2 or len(firstname) > 35:
                messagebox.showerror("Bad data", "Please enter a reasonable first name length between 2 and 35 characters")
                return
            if len(surname) < 2 or len(surname) > 35:
                messagebox.showerror("Bad data", "Please enter a reasonable surname length between 2 and 35 characters")
                return
            # type check on names to ensure only letters
            if re.fullmatch(r"[a-zA-Z ]*", firstname) is None:
                messagebox.showerror("Bad data", "Please enter a firstname using only letters")
                return
            if re.fullmatch(r"[a-zA-Z ]*", surname) is None:
                messagebox.showerror("Bad data", "Please enter a surname using only letters")
                return
            
            self.controller.db.update_player(player[0], firstname, surname, age)

            # showing message saying success
            messagebox.showinfo("title", "Player Updated!")

            win.destroy()
            self.show_results(self.controller.db.read_player_data())

        # function to delete the data, and then go back
        def delete_player():
            confirmed = messagebox.askokcancel("Confirm", "Are you sure you want to delete this player?", default="cancel")
            if confirmed:
                did_work = self.controller.db.delete_player(player[0])
                if did_work:
                    messagebox.showinfo("Success", "Player deleted!")
                else:
                    messagebox.showerror("Failed", "Could not delete the player at this time.")
                    return
                win.destroy()
                self.show_results(self.controller.db.read_player_data())
            
        # buttons to cancel, delete and update
        # cancel just closes the window
        AnimatedButton(
            win, text="Cancel", command=win.destroy,
            width=80, base_colour=FC.base, hover_colour=FC.cancel
        ).grid(row=3, column=0, padx=(15,0), pady=(10,15))

        # deletes the player by first opening a confirmation window
        AnimatedButton(
            win, text="Delete", command=delete_player, hover_cursor="pirate",
            width=80, base_colour=FC.red[0], hover_colour=FC.red[1]
        ).grid(row=3, column=1, padx=(15,20), pady=(10,15))

        # updates the player by first validating the data
        AnimatedButton(
            win, text="Update", command=update_player, hover_cursor="mouse",
            width=80, base_colour=FC.green[0], hover_colour=FC.green[1]
        ).grid(row=3, column=2, padx=(0,20), pady=(10,15))

    # function to display the search results
    def show_results(self, results: list[tuple[str, str, str, int]]):
        # first clear current results
        self.clear_results()
        
        # if no items found for query then display this message
        if not results:
            # if no players in database then show that message, otherwise no players in search results show different message
            if self.controller.db.get_player_count() == 0:
                msg = "You haven't created any players yet.\nClick the create button above!"
            else:
                msg = "No players found."
            ttk.Label(self.results_frame, text=msg).pack(pady=10)
            return

        # creating a row with the text for each result
        # adding extra padding at the bottom of last row
        # binding the name to open edit view if in edit mode otherwise statistics view with the player data
        # name is underlined on hover
        for row in results:
            name = ttk.Label(self.results_frame, text=f"{row[1]} {row[2]}", anchor="center")
            # padding of 3 between each row
            name.pack(pady=(3 if results.index(row) != len(results)-1 else (3,20)))
            name.bind("<Button-1>", lambda e, r=row: self.open_edit_player(r) if self.edit_mode else self.controller.open_statistics_player(r))
            self.controller.make_hoverable(name)

    # function to clear the search field by deleting content in the text box
    def clear_entry(self, event=None):
        self.search_field.delete(0, tk.END)

    # function to clear the search results by removing all content in that frame
    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    # function to search players
    def search_players(self, event=None):
        # scrolling all the way up to top of search results
        self.canvas.yview_moveto(0)

        # fetching query
        query = self.search_field.get().strip()

        # if query is blank then fetch all players
        # else fetch the players for the query
        if query == "":
            results = self.controller.db.read_player_data()
        else:
            results = self.controller.db.search_players(query)
        self.show_results(results)

    # when the clear search button pressed, clear the textbox and then load all players
    def remove_search(self):
        self.clear_entry()
        self.show_results(self.controller.db.read_player_data())