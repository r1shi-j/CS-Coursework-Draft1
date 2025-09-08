import tkinter as tk
from tkinter import ttk
from storage import Database

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        # self.master.protocol("WM_DELETE_WINDOW", self.on_app_close)
        self.db = Database()
        self.db.connect()
        self.players_data = self.db.read_data()

        self.create_styling()
        self.create_layout()
        self.frames = {}
        self.create_navbar()
        self.create_pages()
        self.show_frame("Tournaments")

    def on_app_close(self):
        print("attempted close")

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
        for F in (TournamentsPage, PlayersPage, CircuitsPage, StatisticsPage):
            page_name = F.__name__.replace("Page", "")
            frame = F(self.container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class TournamentsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        # self.controller = controller
        ttk.Label(self, text="Tournaments Page", font=("Arial", 14)).pack(pady=20)


class PlayersPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Players Page", font=("Arial", 14)).pack(pady=20)

        self.build_search_view()

    def build_search_view(self):
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Search players:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.search_field = ttk.Entry(form_frame, width=20)
        self.search_field.grid(row=0, column=1, padx=5, pady=2)

        self.search_field.bind("<KeyRelease>", self.search_players)

        rmv_search_btn = ttk.Button(form_frame, text="Clear", command=self.remove_search)
        rmv_search_btn.grid(row=1, column=3, columnspan=1, pady=10)
        # remove remove search button
        # adding real time searching properly
        # for now have to search full word instead of showing part of it

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(fill="both", expand=True)

        self.show_results(self.controller.db.read_data())

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

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
            ttk.Label(row_frame, text=row[3], width=5, anchor="w").pack(side="left")

    def search_players(self, event=None):
        query = self.search_field.get().strip()
        if query == "":
            results = self.controller.db.read_data()
        else:
            results = self.controller.db.search_players(query)
        self.show_results(results)

    def remove_search(self):
        self.search_field.delete(0, tk.END)
        self.show_results(self.controller.db.read_data())


class CircuitsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Circuits Page", font=("Arial", 14)).pack(pady=20)


class StatisticsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Statistics Page", font=("Arial", 14)).pack(pady=20)