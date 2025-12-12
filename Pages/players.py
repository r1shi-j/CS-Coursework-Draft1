import tkinter as tk
from tkinter import ttk, messagebox

class PlayersPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller):
        super().__init__(parent)
        self.controller = controller
        self.edit_mode = False
        self.build_view()

    def block_window_closure(self): return

    # building the players view homepage with buttons to create and edit players, search bar and list of players
    def build_view(self):
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack()
        
        # creating the title
        title_frame = ttk.Frame(self.form_frame)
        title_frame.pack(pady=(10, 5))
        ttk.Label(title_frame, text="Players Dashboard", font=("TkDefaultFont", 14, "bold")).pack()
        
        # action buttons frame and buttons
        buttons_frame = ttk.Frame(self.form_frame)
        buttons_frame.pack(pady=(5, 10))

        self.create_btn = ttk.Button(buttons_frame, text="Create Player", command=self.open_create_player_view, style="UnHover.TButton", cursor="plus")
        self.create_btn.pack(side="left", padx=10, ipadx=10)
        self.controller.make_hoverable_btn(self.create_btn, "Hover", "UnHover")

        edit_btn = ttk.Button(buttons_frame, text="Edit Player", command=self.toggle_edit_mode, style="UnHover.TButton", cursor="spraycan")
        edit_btn.pack(side="left", padx=10, ipadx=10)
        self.controller.make_hoverable_btn(edit_btn, "Hover", "UnHover")

        # creating the search bar frame
        search_frame = ttk.Frame(self.form_frame)
        search_frame.pack(pady=(5, 10))

        # subtitle, search field and clear button
        # binding keyboard buttons to clear and unfocus search field, with every key release triggering a search for real time searching
        ttk.Label(search_frame, text="Search players:").pack(side="left", padx=5)
        vcmd = (search_frame.register(self.controller.validate_only_letters_numbers), "%P")
        self.search_field = ttk.Entry(search_frame, width=20, validate="key", validatecommand=vcmd)
        self.search_field.pack(side="left", padx=5)
        self.search_field.bind("<KeyRelease>", self.search_players)
        self.search_field.bind("<Command-BackSpace>", self.clear_entry)
        self.search_field.bind("<Escape>", lambda e: self.search_field.focus_set() or self.focus())
        self.clear_results_btn = ttk.Button(search_frame, text="⌫", width=2, command=self.remove_search, cursor="pirate")
        self.clear_results_btn.pack(side="left", padx=5)

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
    def open_create_player_view(self):
        # creating a small pop up window for data entry
        # blocking action on other windows, and blocking window closure using red x
        win = tk.Toplevel(self)
        win.title("Create Player")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)

        vcmd_letters = (win.register(self.controller.validate_only_letters), "%P")
        vcmd_num = (win.register(self.controller.validate_only_numbers), "%P")

        # functions to clear the textfield when command backspace pressed
        def clear_fname(event=None):
            firstname.delete(0, tk.END)
        def clear_sname(event=None):
            surname.delete(0, tk.END)
        def clear_age(event=None):
            firstname.delete(0, tk.END)

        # text box for first name
        ttk.Label(win, text="First name:").grid(row=0, column=0, padx=10, pady=(16,8), sticky="e")
        firstname = ttk.Entry(win, validate="key", validatecommand=vcmd_letters)
        firstname.grid(row=0, column=1, padx=(5,20), pady=(16,8))
        firstname.bind("<Escape>", lambda e: win.focus())
        firstname.bind("<Command-BackSpace>", clear_fname)

        # text box for surname
        ttk.Label(win, text="Surname:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        surname = ttk.Entry(win, validate="key", validatecommand=vcmd_letters)
        surname.grid(row=1, column=1, padx=(5,20), pady=8)
        surname.bind("<Escape>", lambda e: win.focus())
        surname.bind("<Command-BackSpace>", clear_sname)

        # text box for age
        ttk.Label(win, text="Age:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        age = ttk.Entry(win, validate="key", validatecommand=vcmd_num)
        age.grid(row=2, column=1, padx=(5,20), pady=8)
        age.bind("<Escape>", lambda e: win.focus())
        age.bind("<Command-BackSpace>", clear_age)

        # adding the player to the database, and then closing the window and refreshing the player view so that the new player is present
        def create_player():
            fname = firstname.get()
            sname = surname.get()
            dage = age.get()
            if fname == "" or sname == "" or dage == "":
                messagebox.showerror("Missing Info", "Please fill in all fields.")
                return
            self.controller.db.create_player(fname, sname, int(dage))
            win.destroy()
            self.show_results(self.controller.db.read_player_data())

        # buttons to cancel or create
        # cancel closes this window, and create runs the above function
        # when hovers over, the text is underlined
        cancel_btn = ttk.Button(win, text="Cancel", command=win.destroy, style="UnHover.TButton", cursor="mouse")
        cancel_btn.grid(row=3, column=0, padx=(20,0), pady=(10,16), ipadx=10, sticky="e")
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        create_btn = ttk.Button(win, text="Create", command=create_player, style="UnHoverSubmit.TButton", cursor="mouse")
        create_btn.grid(row=3, column=1, padx=(0,20), pady=(10,16), ipadx=10, sticky="e")
        self.controller.make_hoverable_btn(create_btn, "HoverSubmit", "UnHoverSubmit")

    # function to toggle edit mode
    # when going into edit mode, disable create button, search field and clear results button
    # when going out of edit mode, enable them again
    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.create_btn["state"] = "disabled"
            self.create_btn["cursor"] = "arrow"
            self.search_field["state"] = "disabled"
            self.clear_results_btn["state"] = "disabled"
            self.clear_results_btn["cursor"] = "arrow"
        else:
            self.create_btn["state"] = "normal"
            self.create_btn["cursor"] = "crosshair"
            self.search_field["state"] = "normal"
            self.clear_results_btn["state"] = "normal"
            self.clear_results_btn["cursor"] = "pirate"

    # opens the edit player view
    def open_edit_player_view(self, player: tuple[str, str, str, int]):
        # creating a small pop up window for data entry
        # blocking action on other windows, and blocking window closure using red x
        win = tk.Toplevel(self)
        win.title("Edit Player")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)

        vcmd_letters = (win.register(self.controller.validate_only_letters), "%P")
        vcmd_num = (win.register(self.controller.validate_only_numbers), "%P")

        # functions to clear the textfield when command backspace pressed
        def clear_fname(event=None):
            firstname.delete(0, tk.END)
        def clear_sname(event=None):
            surname.delete(0, tk.END)
        def clear_age(event=None):
            firstname.delete(0, tk.END)

        # text box for first name, prefilling with the original data
        ttk.Label(win, text="First name:").grid(row=0, column=0, padx=10, pady=(16,8), sticky="e")
        firstname = ttk.Entry(win, validate="key", validatecommand=vcmd_letters)
        firstname.insert(0, player[1])
        firstname.grid(row=0, column=1, columnspan=2, padx=(5,20), pady=(16,8))
        firstname.bind("<Escape>", lambda e: win.focus())
        firstname.bind("<Command-BackSpace>", clear_fname)

        # text box for surname, prefilling with the original data
        ttk.Label(win, text="Surname:").grid(row=1, column=0, padx=10, pady=8, sticky="e")
        surname = ttk.Entry(win, validate="key", validatecommand=vcmd_letters)
        surname.insert(0, player[2])
        surname.grid(row=1, column=1, columnspan=2, padx=(5,20), pady=8)
        surname.bind("<Escape>", lambda e: win.focus())
        surname.bind("<Command-BackSpace>", clear_sname)

        # text box for age, prefilling with the original data
        ttk.Label(win, text="Age:").grid(row=2, column=0, padx=10, pady=8, sticky="e")
        age = ttk.Entry(win, validate="key", validatecommand=vcmd_num)
        age.insert(0, player[3])
        age.grid(row=2, column=1, columnspan=2, padx=(5,20), pady=8)
        age.bind("<Escape>", lambda e: win.focus())
        age.bind("<Command-BackSpace>", clear_age)

        # function to update the data, and then go back
        def update_player():
            fname = firstname.get()
            sname = surname.get()
            dage = age.get()
            if fname == "" or sname == "" or dage == "":
                messagebox.showerror("Missing Info", "Please fill in all fields.")
                return
            self.controller.db.update_player(player[0], fname, sname, int(dage))
            win.destroy()
            self.show_results(self.controller.db.read_player_data())

        # function to delete the data, and then go back
        def delete_player():
            confirm = messagebox.askokcancel("Confirm", "Are you sure you want to delete this player?", default="cancel")
            if confirm:
                woroked = self.controller.db.delete_player(player[0])
                if not woroked:
                    messagebox.showinfo("Failed", "Could not delete the player at this time.")
                win.destroy()
                self.show_results(self.controller.db.read_player_data())
            
        # buttons to cancel, delete and update
        # cancel just closes the window
        # when hovers over, the text is underlined
        cancel_btn = ttk.Button(win, text="Cancel", command=win.destroy, style="UnHover.TButton", cursor="mouse")
        cancel_btn.grid(row=3, column=0, padx=(20,0), pady=(10,16), sticky="e")
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        delete_btn = ttk.Button(win, text="Delete", command=delete_player, style="UnHoverDelete.TButton", cursor="mouse")
        delete_btn.grid(row=3, column=1, padx=(0,0), pady=(10,16), sticky="e")
        self.controller.make_hoverable_btn(delete_btn, "HoverDelete", "UnHoverDelete")

        update_btn = ttk.Button(win, text="Update", command=update_player, style="UnHoverSubmit.TButton", cursor="mouse")
        update_btn.grid(row=3, column=2, padx=(0,20), pady=(10,16), sticky="e")
        self.controller.make_hoverable_btn(update_btn, "HoverSubmit", "UnHoverSubmit")

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
            name.pack(pady=(2 if results.index(row) != len(results)-1 else (2,20)))
            name.bind("<Button-1>", lambda e, r=row: self.open_edit_player_view(r) if self.edit_mode else self.controller.open_statistics_player(r))
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