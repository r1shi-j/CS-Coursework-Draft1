import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import datetime
from collections import defaultdict
from storage import create_uuid

class TournamentsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Tournaments Page", font=("Arial", 14)).pack(pady=20)

        self.build_view()

    def block_window_closure(self): return

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
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

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
            self.controller.db.create_gps_for_tournament(new_t_id, tournament_players)
            self.refresh_tournaments()
            self.open_tournament_overview(new_t_id)
            win.destroy()

        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=5, column=0, pady=10)
        ttk.Button(win, text="Create", command=create_tournament).grid(row=5, column=1, pady=10)

    def open_edit_tournament_view(self, t_id: str):
        win = tk.Toplevel(self)
        win.title("Edit Tournament")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        original_date_str = self.controller.db.read_tournament_date(t_id)
        original_date = datetime.datetime.strptime(original_date_str, "%d/%m/%y").date()

        datepicker_frame = ttk.LabelFrame(win, text="Date")
        datepicker_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        mindate = original_date - datetime.timedelta(days=365)
        maxdate = original_date + datetime.timedelta(days=365)

        cal = Calendar(
            win,
            selectmode="day",
            year=original_date.year,
            month=original_date.month,
            day=original_date.day,
            mindate=mindate,
            maxdate=maxdate,
            foreground="black",
            selectforeground="red",
            selectbackground="blue",
            headersforeground="black",
            normalforeground="black",
            weekendforeground="black",
            othermonthforeground="gray"
        )
        cal.grid(row=0, column=1, padx=5, pady=5)

        def chosen_date() -> str: 
            return datetime.datetime.strptime(cal.get_date(), '%m/%d/%y').strftime('%d/%m/%y')
        
        selected_date_label = ttk.Label(win, text=f"Selected Date: {chosen_date()}")
        selected_date_label.grid(row=1, column=1, padx=5, pady=5)

        def on_date_selected(event):
            selected_date_label.config(text=f"Selected Date: {chosen_date()}")

        cal.bind("<<CalendarSelected>>", on_date_selected)

        tournament_players = self.controller.db.read_tournament_players(t_id)
        removed_players = []
        added_players = []

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
        refresh_current_players()

        def remove_player(player):
            tournament_players.remove(player)
            removed_players.append(player[0])
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
                added_players.append(player[0])
            refresh_current_players()

        search_var.trace_add("write", update_search)

        t_type_frame = ttk.LabelFrame(win, text="Tournament Type")
        t_type_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        selected_type = tk.StringVar()
        current_type_id = self.controller.db.read_tournament_type(t_id)
        self.build_tournament_type_section(t_type_frame, selected_type, current_type_id)

        add_type_btn = ttk.Button(
            t_type_frame,
            text="+",
            command=lambda: self.open_add_type_view(t_type_frame, selected_type)
        )
        add_type_btn.pack(side="top", anchor="ne", padx=5, pady=2)

        def go_back():
            self.open_tournament_overview(t_id)
            win.destroy()

        def update_tournament():
            self.controller.db.update_tournament(t_id, chosen_date(), len(tournament_players), selected_type.get())

            original_players = [p[0] for p in self.controller.db.read_tournament_players(t_id)]
            for player in added_players:
                if player not in original_players:
                    self.controller.db.add_player_to_tournament(t_id, player)
                
            for player in removed_players:
                if player in original_players:
                    self.controller.db.remove_player_from_tournament(t_id, player)
                
            self.refresh_tournaments()
            go_back()

        ttk.Button(win, text="Discard Changes", command=go_back).grid(row=5, column=0, pady=10)
        # ttk.Button(win, text="Delete", command=win.destroy).grid(row=5, column=0, pady=10)
        ttk.Button(win, text="Update", command=update_tournament).grid(row=5, column=1, pady=10)

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

            winner = self.controller.db.read_tournament_winner(row[0])
            if winner:
                tk.Label(row_frame, text=winner[1], width=20, anchor="w", bg=bg).pack(side="left")

            row_frame.bind("<Button-1>", lambda e, tid=row[0]: self.open_tournament_overview(tid))
            for child in row_frame.winfo_children():
                child.bind("<Button-1>", lambda e, tid=row[0]: self.open_tournament_overview(tid))

    # change to race and then gp, or keep same and use recursion when race 4
    def open_input_race_results(self, gp_id: str, t_id: str):
        race_count = self.controller.db.get_race_count_in_gp(gp_id)
        win = tk.Toplevel(self)
        win.title(f"Input Race [{race_count + 1}/4] Results")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        circuits = self.controller.db.read_circuit_data()
        circuit_names = [c[1] for c in circuits]
        name_to_circuit = {c[1]: c for c in circuits}

        ttk.Label(win, text="Select Circuit:").grid(row=0, column=0, padx=5, pady=5)

        circuit_var = tk.StringVar()
        circuit_dropdown = ttk.Combobox(
            win,
            textvariable=circuit_var,
            values=circuit_names,
            state="readonly"
        )
        circuit_dropdown.grid(row=0, column=1, padx=5, pady=5)
        
        players = self.controller.db.read_grand_prix_players(gp_id)
        result_vars = {}
        
        for row, p in enumerate(players):
            ttk.Label(win, text=p[1]).grid(row=1+row, column=0, padx=5, pady=5, sticky="w")

            result_var = tk.StringVar()
            result_dropdown = ttk.Combobox(
                win,
                textvariable=result_var,
                values=[str(i) for i in range(1, 13)],
                state="readonly",
                width=5
            )
            result_dropdown.grid(row=1+row, column=1, padx=5, pady=5)
            result_vars[p[0]] = result_var

        # validation that all fields must be entered, and that results can't be the same
        def insert_results():
            chosen_name = circuit_var.get()
            if chosen_name:
                chosen_circuit = name_to_circuit[chosen_name]
                c_id = chosen_circuit[0]
            players_results = [(pid, int(var.get())) for pid, var in result_vars.items()]
            self.controller.db.create_race(gp_id, c_id, players_results)
            new_race_count = self.controller.db.get_race_count_in_gp(gp_id)
            if new_race_count == 4: self.open_input_gp_results(gp_id, t_id)
            win.destroy()
            self.refresh_brackets(t_id)

        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=5, column=0, pady=10, sticky="w")
        ttk.Button(win, text="Insert Resuts", command=insert_results).grid(row=5, column=1, pady=10, sticky="w")
    
    def open_input_gp_results(self, gp_id: str, t_id: str):
        win = tk.Toplevel(self)
        win.title("Input Grand Prix Results")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        players = self.controller.db.read_grand_prix_players(gp_id)
        result_vars = {}

        for row, p in enumerate(players):
            ttk.Label(win, text=f"{p[1]} {p[2]}").grid(row=row, column=0, padx=5, pady=5, sticky="w")

            result_var = tk.StringVar()
            result_dropdown = ttk.Combobox(
                win,
                textvariable=result_var,
                values=[str(i) for i in range(1, 13)],
                state="readonly",
                width=5
            )
            result_dropdown.grid(row=row, column=1, padx=5, pady=5)
            result_vars[p[0]] = result_var

        def save_gp_results():
            for pid, var in result_vars.items():
                if var.get():
                    self.controller.db.cursor.execute(
                        "UPDATE GrandPrixParticipation SET grandprix_result = ? WHERE grandprix_id = ? AND player_id = ?",
                        (int(var.get()), gp_id, pid)
                    )
            self.controller.db.connection.commit()
            
            top_players = self.controller.db.find_winners_for_gp(gp_id)
            new_gp_id = self.controller.db.find_next_gp_id(gp_id)
            if new_gp_id == "Tournament finished":
                winner = self.controller.db.calculate_tournament_winner(gp_id)
                print(winner)
                ## TODO: set tournaemnt result TournamentParticipation for all players
                self.controller.db.cursor.execute("UPDATE TournamentParticipation SET tournament_result = 1 WHERE tournament_id = ? AND player_id = ?", (t_id, winner[0]))
                self.controller.db.connection.commit()
            else:
                self.controller.db.add_winners_to_gp(top_players, new_gp_id)

            win.destroy()
            self.refresh_brackets(t_id)

        ttk.Button(win, text="Complete Grand Prix", command=save_gp_results).grid(row=5, column=0, pady=10)
        
    def open_tournament_brackets(self, t_id: str):
        self.bracket_win = tk.Toplevel(self)
        self.bracket_win.title("Tournament Brackets")
        self.bracket_win.grab_set()
        self.bracket_win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        self.brackets_container = ttk.Frame(self.bracket_win)
        self.brackets_container.pack(fill="both", expand=True)

        self._build_brackets(t_id)

    def _build_brackets(self, t_id: str):
        for widget in self.brackets_container.winfo_children():
            widget.destroy()

        grand_prix_list = self.controller.db.read_grand_prix(t_id)
        rounds_dict = defaultdict(list)

        for gp in grand_prix_list:
            gp_id, round_num, inverse, bracket, continuers = gp
            rounds_dict[round_num].append(gp)

        round_numbers = sorted([r if r is not None else 999 for r in rounds_dict.keys()])
        rounds_reversed = sorted(round_numbers, reverse=True)[1:]
        rounds_joined = round_numbers + rounds_reversed
        final_index = rounds_joined.index(999)

        def make_frame(gpi, round_frame):
            gp_id, round_num, inverse, bracket, continuers = gpi
            gp_players = self.controller.db.read_grand_prix_players(gp_id)

            currentno = self.controller.db.get_race_count_in_gp(gp_id)
            if currentno == 0:
                line = "Not started"
            elif currentno == 4:
                line = ""
            else:
                line = f"{currentno}/4 Races Completed"
            ttk.Label(round_frame, text=line, anchor="w").pack(fill="x")

            match_frame = ttk.Frame(round_frame, relief="solid", borderwidth=1, padding=5)
            match_frame.pack(pady=10, fill="x")

            style = ttk.Style()
            style.configure("Black.TLabel", foreground="#000000")
            style.configure("Green.TLabel", foreground="#11DF11")

            for name in gp_players:
                color = "Black.TLabel"
                if self.controller.db.get_race_count_in_gp(gp_id) == 4:
                    wins = self.controller.db.find_winners_for_gp(gp_id)
                    if type(wins) == tuple:
                        if name == wins:
                            color = "Green.TLabel"
                    else:
                        fmap = [p[0] for p in wins]
                        if name[0] in fmap: 
                            color = "Green.TLabel"

                ttk.Label(match_frame, text=name[1], anchor="w", style=color).pack(fill="x")

            # ttk.Label(match_frame, text=f"Grand Prix {gp_id[:4]}", anchor="w").pack(fill="x")
            # ttk.Label(match_frame, text=f"Continuers: {continuers}", anchor="w").pack(fill="x")

            # add condition that all previous sections must be complete (eg round 1 complete for round 2 buttons to be shown)
            if currentno < 4:
                ttk.Button(round_frame, text="Input results", command=lambda: self.open_input_race_results(gp_id, t_id)).pack(fill="x")

        for col, round_num in enumerate(rounds_joined):
            title = f"Round {round_num}" if round_num != 999 else "Final"
            round_frame = ttk.LabelFrame(self.brackets_container, text=title)
            round_frame.grid(row=0, column=col, padx=40, pady=20, sticky="n")

            rn = round_num
            if rn == 999: rn = None

            for gp in rounds_dict[rn]:
                if col < final_index:
                    if gp[2] == False: make_frame(gp, round_frame)
                elif col == final_index:
                    make_frame(gp, round_frame)
                else:
                    if gp[2] == True: make_frame(gp, round_frame)

        winner = self.controller.db.read_tournament_winner(t_id)
        if winner is not None:
            winner_label = ttk.Label(self.brackets_container, text=f"Winner: {winner[1]}", font=("Arial", 12, "bold"))
            winner_label.grid(row=1, column=len(rounds_joined)//2, pady=20)

        def go_back():
            self.open_tournament_overview(t_id)
            self.bracket_win.destroy()

        ttk.Button(self.brackets_container, text="Back", command=go_back).grid(row=2, column=0, pady=10, sticky="w")

    def refresh_brackets(self, t_id: str):
        self._build_brackets(t_id)
    
    def open_tournament_overview(self, t_id: str):
        win = tk.Toplevel(self)
        win.title("Tournament Overview")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        def open_brackets():
            self.open_tournament_brackets(t_id)
            win.destroy()

        def open_settings():
            self.open_edit_tournament_view(t_id)
            win.destroy()

        ttk.Label(win, text="Date:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(win, text="Brackets", command=open_brackets).grid(row=0, column=1, pady=10)
        ttk.Label(win, text="Player count:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(win, text="Round:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Label(win, text="Players competing:").grid(row=3, column=0, padx=5, pady=5)
        ttk.Label(win, text="Players eliminated:").grid(row=4, column=0, padx=5, pady=5)

        ttk.Button(win, text="Back", command=win.destroy).grid(row=5, column=0, pady=10)
        ttk.Button(win, text="Settings", command=open_settings).grid(row=5, column=1, pady=10)
        
    def build_tournament_type_section(self, parent, selected_type, current_type_id=None):
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
            if current_type_id == t_type[0]:
                selected_type.set(t_type[0])
            
    def open_add_type_view(self, parent_frame, selected_type):
        win = tk.Toplevel(self)
        win.title("Add Tournament Type")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

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