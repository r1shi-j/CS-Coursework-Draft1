import tkinter as tk
from tkinter import ttk

class PlayersPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Players Page", font=("Arial", 14)).pack()

        self.edit_mode = False
        self.build_view()

    def build_view(self):
        # each name should be a button when clicked goes to stats view with that player
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=5)

        create_btn = ttk.Button(action_frame, text="Create Player", command=self.open_create_player_view)
        create_btn.pack(side="left", padx=5)

        edit_btn = ttk.Button(action_frame, text="Edit Player", command=self.enable_edit_mode)
        edit_btn.pack(side="left", padx=5)
        
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack(pady=10)

        ttk.Label(self.form_frame, text="Search players:").grid(row=0, column=0, padx=5, pady=2, sticky="e")

        self.search_field = ttk.Entry(self.form_frame, width=20)
        self.search_field.grid(row=0, column=1, padx=5, pady=2)
        
        self.search_field.bind("<KeyRelease>", self.search_players)
        self.search_field.bind("<Command-BackSpace>", self.clear_entry)

        rmv_search_btn = ttk.Button(self.form_frame, text="⌫", width=2, command=self.remove_search)
        rmv_search_btn.grid(row=0, column=2, padx=2)

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(fill="both", expand=True)

        self.show_results(self.controller.db.read_player_data())

    def open_create_player_view(self):
        win = tk.Toplevel(self)
        win.title("Create Player")
        win.grab_set()

        ttk.Label(win, text="First name:").grid(row=0, column=0, padx=5, pady=5)
        firstname = ttk.Entry(win)
        firstname.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(win, text="Surname:").grid(row=1, column=0, padx=5, pady=5)
        surname = ttk.Entry(win)
        surname.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(win, text="Age:").grid(row=2, column=0, padx=5, pady=5)
        age = ttk.Entry(win)
        age.grid(row=2, column=1, padx=5, pady=5)

        def create_player():
            self.controller.db.add_player(firstname.get(), surname.get(), int(age.get()))
            win.destroy()
            self.show_results(self.controller.db.read_player_data())

        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=3, column=0, pady=10)
        ttk.Button(win, text="Create", command=create_player).grid(row=3, column=1, pady=10)

    def enable_edit_mode(self):
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.form_frame.pack_forget()
        else:
            self.form_frame.pack(pady=10, before=self.results_frame)
        self.show_results(self.controller.db.read_player_data())

    def show_results(self, results):
        self.clear_results()
        if not results:
            ttk.Label(self.results_frame, text="No players found.").pack(pady=10)
            return

        for row in results:
            row_frame = ttk.Frame(self.results_frame)
            row_frame.pack(fill="x", pady=2)

            ttk.Label(row_frame, text=row[1], width=20, anchor="w").pack(side="left")
            ttk.Label(row_frame, text=row[2], width=20, anchor="w").pack(side="left")

            if self.edit_mode:
                edit_btn = ttk.Button(row_frame, text="✎", width=2, command=lambda r=row: self.open_edit_player_view(r))
                edit_btn.pack(side="left", padx=5)

    def open_edit_player_view(self, player):
        win = tk.Toplevel(self)
        win.title("Edit Player")
        win.grab_set()

        ttk.Label(win, text="First name:").grid(row=0, column=0, padx=5, pady=5)
        firstname = ttk.Entry(win)
        firstname.insert(0, player[1])
        firstname.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(win, text="Surname:").grid(row=1, column=0, padx=5, pady=5)
        surname = ttk.Entry(win)
        surname.insert(0, player[2])
        surname.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(win, text="Age:").grid(row=2, column=0, padx=5, pady=5)
        age = ttk.Entry(win)
        age.insert(0, player[3])
        age.grid(row=2, column=1, padx=5, pady=5)

        def update_player():
            self.controller.db.update_player(player[0], firstname.get(), surname.get(), int(age.get()))
            win.destroy()
            self.show_results(self.controller.db.read_player_data())

        def delete_player():
            self.controller.db.delete_player(player[0])
            win.destroy()
            self.show_results(self.controller.db.read_player_data())

        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=3, column=0, pady=10)
        ttk.Button(win, text="Delete", command=delete_player).grid(row=3, column=1, pady=10)
        ttk.Button(win, text="Update", command=update_player).grid(row=3, column=2, pady=10)
        
    def clear_entry(self, event=None):
        self.search_field.delete(0, tk.END)

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def search_players(self, event=None):
        query = self.search_field.get().strip()
        if query == "":
            results = self.controller.db.read_player_data()
        else:
            results = self.controller.db.search_players(query)
        self.show_results(results)

    def remove_search(self):
        self.search_field.delete(0, tk.END)
        self.show_results(self.controller.db.read_player_data())