import tkinter as tk
from tkinter import ttk

class PlayersPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Players Page", font=("Arial", 14)).pack()

        self.edit_mode = False
        self.build_view()

    def block_window_closure(self): return

    def build_view(self):
        # TODO: convert to scroll view
        # TODO: each name should be a button when clicked goes to stats view with that player
        # creating a seperate frame for the action buttons
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=5)

        # adding create and edit buttons to the action frame
        create_btn = ttk.Button(action_frame, text="Create Player", command=self.open_create_player_view)
        create_btn.pack(side="left", padx=5)

        edit_btn = ttk.Button(action_frame, text="Edit Player", command=self.toggle_edit_mode)
        edit_btn.pack(side="left", padx=5)
        
        # creating another frame for the rest of the view
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack(pady=10)

        ttk.Label(self.form_frame, text="Search players:").grid(row=0, column=0, padx=5, pady=2, sticky="e")

        # creating the search field textbox
        self.search_field = ttk.Entry(self.form_frame, width=20)
        self.search_field.grid(row=0, column=1, padx=5, pady=2)
        
        # when any key is pressed it will search which is for real time searching
        # binding cmd del to clear search field
        self.search_field.bind("<KeyRelease>", self.search_players)
        self.search_field.bind("<Command-BackSpace>", self.clear_entry)

        # clear search button
        rmv_search_btn = ttk.Button(self.form_frame, text="⌫", width=2, command=self.remove_search)
        rmv_search_btn.grid(row=0, column=2, padx=2)

        # the container for the search results
        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(fill="both", expand=True)

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

        # text box for first name
        ttk.Label(win, text="First name:").grid(row=0, column=0, padx=5, pady=5)
        firstname = ttk.Entry(win)
        firstname.grid(row=0, column=1, padx=5, pady=5)

        # text box for surname
        ttk.Label(win, text="Surname:").grid(row=1, column=0, padx=5, pady=5)
        surname = ttk.Entry(win)
        surname.grid(row=1, column=1, padx=5, pady=5)

        # text box for age
        ttk.Label(win, text="Age:").grid(row=2, column=0, padx=5, pady=5)
        age = ttk.Entry(win)
        age.grid(row=2, column=1, padx=5, pady=5)

        # adding the player to the database, and then closing the window and refreshing the player view so that the new player is present
        def create_player():
            self.controller.db.add_player(firstname.get(), surname.get(), int(age.get()))
            win.destroy()
            self.show_results(self.controller.db.read_player_data())

        # buttons to cancel or create
        # cancel closes this window, and create runs the above function
        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=3, column=0, pady=10)
        ttk.Button(win, text="Create", command=create_player).grid(row=3, column=1, pady=10)

    # function to toggle edit mode
    # when going into edit mode, hiding the search field frame and clearing it
    # when going out of edit mode, showing the search field frame
    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.form_frame.pack_forget()
            self.clear_entry()
        else:
            self.form_frame.pack(pady=10, before=self.results_frame)
        self.show_results(self.controller.db.read_player_data())

    # function to show results
    def show_results(self, results):
        # first clear current results
        self.clear_results()

        # if no items found for query then display this message
        if not results:
            ttk.Label(self.results_frame, text="No players found.").pack(pady=10)
            return

        # creating a row with the text for each result
        for row in results:
            row_frame = ttk.Frame(self.results_frame)
            row_frame.pack(fill="x", pady=2)

            # TODO: each player should be a button when clicked goes to stats view for that player
            ttk.Label(row_frame, text=row[1], width=20, anchor="w").pack(side="left")
            ttk.Label(row_frame, text=row[2], width=20, anchor="w").pack(side="left")

            # if in edit mode, then display the edit button
            if self.edit_mode:
                edit_btn = ttk.Button(row_frame, text="✎", width=2, command=lambda r=row: self.open_edit_player_view(r))
                edit_btn.pack(side="left", padx=5)

    # opens the edit player view
    def open_edit_player_view(self, player):
        # creating a small pop up window for data entry
        # blocking action on other windows, and blocking window closure using red x
        win = tk.Toplevel(self)
        win.title("Edit Player")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        # text box for first name, prefilling with the original data
        ttk.Label(win, text="First name:").grid(row=0, column=0, padx=5, pady=5)
        firstname = ttk.Entry(win)
        firstname.insert(0, player[1])
        firstname.grid(row=0, column=1, padx=5, pady=5)

        # text box for surname, prefilling with the original data
        ttk.Label(win, text="Surname:").grid(row=1, column=0, padx=5, pady=5)
        surname = ttk.Entry(win)
        surname.insert(0, player[2])
        surname.grid(row=1, column=1, padx=5, pady=5)

        # text box for age, prefilling with the original data
        ttk.Label(win, text="Age:").grid(row=2, column=0, padx=5, pady=5)
        age = ttk.Entry(win)
        age.insert(0, player[3])
        age.grid(row=2, column=1, padx=5, pady=5)

        # function to update the data, and then go back
        def update_player():
            self.controller.db.update_player(player[0], firstname.get(), surname.get(), int(age.get()))
            win.destroy()
            self.show_results(self.controller.db.read_player_data())

        # function to delete the data, and then go back
        def delete_player():
            self.controller.db.delete_player(player[0])
            win.destroy()
            self.show_results(self.controller.db.read_player_data())

        # buttons to cancel, delete and update
        # cancel just closes the window
        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=3, column=0, pady=10)
        ttk.Button(win, text="Delete", command=delete_player).grid(row=3, column=1, pady=10)
        ttk.Button(win, text="Update", command=update_player).grid(row=3, column=2, pady=10)
    
    # function to clear the search field by deleting content in the text box
    def clear_entry(self, event=None):
        self.search_field.delete(0, tk.END)

    # function to clear the search results by removing all content in that frame
    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    # function to search players
    def search_players(self, event=None):
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