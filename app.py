import tkinter as tk
from tkinter import ttk
from storage import Database
from Pages import tournaments, players, circuits, statistics

# creating the frame
class App(tk.Frame):
    # initialising the database and creating the layout
    # master protocol to run a function when closes window with red x
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
    
    # when close window, first closing the database, and then close window
    def on_app_close(self):
        self.db.close()
        self.master.quit()

    def create_styling(self):
        self.style = ttk.Style()
        self.style.configure("HoverDelete.TButton", foreground="#df3832", font=("TkDefaultFont", 10, "underline"))
        self.style.configure("UnHoverDelete.TButton", foreground="#df3832", font=("TkDefaultFont", 10, "normal"))
        self.style.configure("HoverSubmit.TButton", foreground="#00a2ff", font=("TkDefaultFont", 10, "underline"))
        self.style.configure("UnHoverSubmit.TButton", foreground="#00a2ff", font=("TkDefaultFont", 10, "normal"))
        self.style.configure("Hover.TButton", font=("TkDefaultFont", 10, "underline"))
        self.style.configure("UnHover.TButton", font=("TkDefaultFont", 10, "normal"))

    # creating the layout
    # creates the frame and disables resizing
    def create_layout(self):
        self.master.title("Mario Kart Tournament System")
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

    # creates the navigation bar
    def create_navbar(self):
        self.nav_labels = {}

        # function to make navigation label
        def make_nav_label(parent, text, view_name):
            label = ttk.Label(parent, text=text, font=("TkDefaultFont", 12))
            label.pack(side="left", padx=40)

            # adding underline when hover
            def on_enter(e):
                if self.current_page != view_name:
                    label.configure(font=("TkDefaultFont", 12, "underline"))

            # remove underline when not hovering
            def on_leave(e):
                if self.current_page != view_name:
                    label.configure(font=("TkDefaultFont", 12))

            def on_click(e): self.show_frame(view_name)

            label.bind("<Enter>", on_enter)
            label.bind("<Leave>", on_leave)
            label.bind("<Button-1>", on_click)
            self.nav_labels[view_name] = label
            return label

        # making all the headers
        make_nav_label(self.header_frame, "Tournaments", "Tournaments")
        make_nav_label(self.header_frame, "Players", "Players")
        make_nav_label(self.header_frame, "Circuits", "Circuits")
        make_nav_label(self.header_frame, "Statistics", "Statistics")

        self.current_page = None

    # linking the Pages files to run when clicked on their header
    def create_pages(self):
        for F in (tournaments.TournamentsPage, players.PlayersPage, circuits.CircuitsPage, statistics.StatisticsPage):
            page_name = F.__name__.replace("Page", "")
            frame = F(self.container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    # showing the respective frame when clicked on
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

        # adding or removing the blue font colour to current view title
        for name, label in self.nav_labels.items():
            if name == page_name:
                label.configure(font=("TkDefaultFont", 12, "underline"), foreground="blue")
            else:
                label.configure(font=("TkDefaultFont", 12), foreground="black")

        self.current_page = page_name

    # function to underline a label on hover
    # takes opetional parameters for font size and weight
    def make_hoverable(self, label, size=None, weight=None):
        base_font = ("TkDefaultFont", size if size else 10, weight if weight else "normal")
        hover_font = ("TkDefaultFont", size if size else 10, f"{weight} underline" if weight else "underline")
        label.bind("<Enter>", lambda e: label.config(font=hover_font))
        label.bind("<Leave>", lambda e: label.config(font=base_font))

    def make_hoverable_btn(self, button, h, uh):
        button.bind("<Enter>", lambda e: button.config(style=f"{h}.TButton"))
        button.bind("<Leave>", lambda e: button.config(style=f"{uh}.TButton"))

    # function to open statistics view with player data
    def open_statistics_player(self, player):
        stats_page = self.frames["Statistics"]
        stats_page.load_player_stats(player)
        self.show_frame("Statistics")

    # function to open statistics view with circuit data
    def open_statistics_circuit(self, circuit):
        stats_page = self.frames["Statistics"]
        stats_page.load_circuit_stats(circuit)
        self.show_frame("Statistics")