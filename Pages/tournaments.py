import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry, Calendar
import datetime
from storage import create_uuid

class TournamentsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Tournaments Page", font=("Arial", 14)).pack(pady=20)

        self.build_view()

    def build_view(self):
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=5)

        create_btn = ttk.Button(action_frame, text="Create Tournament", command=self.open_create_tournament_view)
        create_btn.pack(side="left", padx=5)

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.results_frame = ttk.Frame(canvas)
        self.results_frame.pack(fill="both", expand=True)
        canvas_window = canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.results_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        self.refresh_tournaments()

    def open_create_tournament_view(self):
        win = tk.Toplevel(self)
        win.title("Create Tournament")
        win.grab_set()

        datepicker_frame = ttk.LabelFrame(win, text="Date")
        datepicker_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        today = datetime.date.today()
        mindate = today - datetime.timedelta(days=365)
        maxdate = today + datetime.timedelta(days=365)
        cal = Calendar(
            win,
            selectmode="day",
            year=today.year,
            month=today.month,
            day=today.day,
            mindate=mindate,
            maxdate=maxdate,
            foreground="black",         # normal text
            selectforeground="red",   # selected day text
            selectbackground="blue",    # selected day background
            headersforeground="black",  # day names (Mon, Tue...)
            normalforeground="black",   # dates
            weekendforeground="black",    # weekends
            othermonthforeground="gray" # days from prev/next month
        )
        cal.grid(row=0, column=1, padx=5, pady=5)

        def chosen_date() -> str: 
            return datetime.datetime.strptime(cal.get_date(), '%m/%d/%y').strftime('%d/%m/%y')
        
        selected_date_label = ttk.Label(win, text=f"Selected Date: {chosen_date()}")
        selected_date_label.grid(row=1, column=1, padx=5, pady=5)

        def on_date_selected(event):
            selected_date_label.config(text=f"Selected Date: {chosen_date()}")

        cal.bind("<<CalendarSelected>>", on_date_selected)

        tournament_players = []
        ## beacuse tournament hasnt been created no need to sql for add/remove/list

        current_players_frame = ttk.LabelFrame(win, text="Current Players")
        current_players_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        cp_canvas = tk.Canvas(current_players_frame, borderwidth=0)
        cp_scrollbar = ttk.Scrollbar(current_players_frame, orient="vertical", command=cp_canvas.yview)
        cp_list_frame = ttk.Frame(cp_canvas)

        cp_list_frame.bind("<Configure>", lambda e: cp_canvas.configure(scrollregion=cp_canvas.bbox("all")))
        cp_canvas.create_window((0, 0), window=cp_list_frame, anchor="nw")
        cp_canvas.configure(yscrollcommand=cp_scrollbar.set)

        cp_canvas.pack(side="left", fill="both", expand=True)
        cp_scrollbar.pack(side="right", fill="y")

        def refresh_current_players():
            for w in cp_list_frame.winfo_children():
                w.destroy()
            for player in tournament_players:
                row = ttk.Frame(cp_list_frame)
                row.pack(fill="x", pady=1)
                ttk.Label(row, text=player[1], width=20, anchor="w").pack(side="left")
                ttk.Button(row, text="-", command=lambda p=player: remove_player(p)).pack(side="right")

        def remove_player(player):
            tournament_players.remove(player)
            refresh_current_players()

        add_players_frame = ttk.LabelFrame(win, text="Add Players")
        add_players_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        search_var = tk.StringVar()

        search_entry = ttk.Entry(add_players_frame, textvariable=search_var)
        search_entry.pack(fill="x", padx=5, pady=5)

        results_frame = ttk.Frame(add_players_frame)
        results_frame.pack(fill="both", expand=True)

        def update_search(*args):
            for w in results_frame.winfo_children():
                w.destroy()
            if not search_var.get().strip():
                return
            results = self.controller.db.search_players(search_var.get())
            for player in results:
                row = ttk.Frame(results_frame)
                row.pack(fill="x", pady=1)
                ttk.Label(row, text=f"{player[1]} {player[2]}", width=20, anchor="w").pack(side="left")
                ## only allow letters no numbers
                ttk.Button(row, text="+", command=lambda p=player: add_player(p)).pack(side="right")

        def add_player(player):
            if player not in tournament_players:
                tournament_players.append(player)
            refresh_current_players()

        search_var.trace_add("write", update_search)


        t_type_frame = ttk.LabelFrame(win, text="Tournament Type")
        t_type_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        selected_type = tk.StringVar()
        self.build_tournament_type_section(t_type_frame, selected_type)

        add_type_btn = ttk.Button(
            t_type_frame,
            text="+",
            command=lambda: self.open_add_type_view(t_type_frame, selected_type)
        )
        add_type_btn.pack(side="top", anchor="ne", padx=5, pady=2)

        def create_tournament():
            new_t_id = create_uuid()
            self.controller.db.create_tournament(new_t_id, chosen_date(), len(tournament_players), selected_type.get())
            for player in tournament_players:
                self.controller.db.add_player_to_tournament(new_t_id, player[0])
            self.refresh_tournaments()
            win.destroy()

        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=5, column=0, pady=10)
        ttk.Button(win, text="Create", command=create_tournament).grid(row=5, column=1, pady=10)

    def refresh_tournaments(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        results = self.controller.db.read_tournament_data()

        # add column headers
        for i, row in enumerate(results):
            bg = "#f0f0f0" if i % 2 == 0 else "#d9d9d9"  # light grey / slightly darker grey

            row_frame = tk.Frame(self.results_frame, bg=bg, highlightbackground="black", highlightthickness=1)
            row_frame.pack(fill="x", pady=1)

            tk.Label(row_frame, text=row[1], width=20, anchor="w", bg=bg).pack(side="left")

            winner = self.controller.db.find_tournament_winner(row[0])
            if winner:
                tk.Label(row_frame, text=winner[0][1], width=20, anchor="w", bg=bg).pack(side="left")

            row_frame.bind("<Button-1>", lambda e, tid=row[0]: self.open_tournament_detail(tid))
            for child in row_frame.winfo_children():
                child.bind("<Button-1>", lambda e, tid=row[0]: self.open_tournament_detail(tid))

    def open_tournament_detail(self, t_id: str):
        print(f"{t_id} clicked")
    
                
    def build_tournament_type_section(self, parent, selected_type):
        for widget in parent.winfo_children():
            if isinstance(widget, ttk.Radiobutton):
                widget.destroy()

        for t_type in self.controller.db.read_tournament_types():
            desc = f"{t_type[1]} cont, {t_type[2]} GPs, {'Long' if t_type[3] else 'Normal'}"
            rb = ttk.Radiobutton(
                parent,
                text=desc,
                variable=selected_type,
                value=t_type[0]
            )
            rb.pack(anchor="w")
            
    def open_add_type_view(self, parent_frame, selected_type):
        win = tk.Toplevel(self)
        win.title("Add Tournament Type")
        win.grab_set()

        ttk.Label(win, text="Default Continuers:").grid(row=0, column=0, padx=5, pady=5)
        cont_entry = ttk.Entry(win)
        cont_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(win, text="Number of Grand Prix:").grid(row=1, column=0, padx=5, pady=5)
        gp_entry = ttk.Entry(win)
        gp_entry.grid(row=1, column=1, padx=5, pady=5)

        longer_var = tk.BooleanVar()
        ttk.Checkbutton(win, text="Longer Style", variable=longer_var).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        def save_type():
            self.controller.db.add_tournament_type(
                int(cont_entry.get()),
                int(gp_entry.get()),
                longer_var.get()
            )
            win.destroy()
            self.build_tournament_type_section(parent_frame, selected_type)

        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=3, column=0, pady=10)
        ttk.Button(win, text="Save", command=save_type).grid(row=3, column=1, pady=10)