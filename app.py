import tkinter as tk
from tkinter import ttk
from storage import Database
from Pages import tournaments, players, circuits, statistics

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_app_close)
        self.db = Database()
        self.db.connect()
        self.create_styling()
        self.create_layout()
        self.frames = {}
        self.create_navbar()
        self.create_pages()
        self.show_frame("Tournaments")

    def on_app_close(self):
        self.db.close()
        print("saved db")
        self.master.quit()

    def create_styling(self):
        self.style = ttk.Style()

    def create_layout(self):
        self.master.title("Home") ###
        self.master.minsize(600, 400)
        self.master.resizable(False, False)
        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill="both", expand=True)

        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill="x", pady=(15, 5))

        self.separator = ttk.Separator(self.main_frame, orient="horizontal")
        self.separator.pack(fill="x", padx=10, pady=5)

        self.container = ttk.Frame(self.main_frame)
        self.container.pack(fill="both", expand=True)

    def create_navbar(self):
        def make_nav_label(parent, text, view_name):
            label = ttk.Label(parent, text=text, font=("Arial", 12), cursor="hand2")
            label.pack(side="left", padx=40)

            def on_enter(e): label.configure(font=("Arial", 12, "underline"))
            def on_leave(e): label.configure(font=("Arial", 12))
            def on_click(e): self.show_frame(view_name)

            label.bind("<Enter>", on_enter)
            label.bind("<Leave>", on_leave)
            label.bind("<Button-1>", on_click)
            return label

        make_nav_label(self.header_frame, "Tournaments", "Tournaments")
        make_nav_label(self.header_frame, "Players", "Players")
        make_nav_label(self.header_frame, "Circuits", "Circuits")
        make_nav_label(self.header_frame, "Statistics", "Statistics")

    def create_pages(self):
        for F in (tournaments.TournamentsPage, players.PlayersPage, circuits.CircuitsPage, statistics.StatisticsPage):
            page_name = F.__name__.replace("Page", "") # checl if worlks
            frame = F(self.container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()