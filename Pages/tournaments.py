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

    # this function is used to do nothing and block child window closure
    def block_window_closure(self): return

    # function to build the tournaments list
    def build_view(self):
        # frame for the create button
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=5)

        # create tournament button
        create_btn = ttk.Button(action_frame, text="Create Tournament", command=self.open_create_tournament_view)
        create_btn.pack(side="left", padx=5)

        # initialising the sort options
        self.sort_options = ("Date", "ASC")

        # function to change the internal property tracking the sort option and order
        # after the change it refreshes the view so that the sorted list is shown
        def change_order(property: str):
            if self.sort_options[0] == property:
                self.sort_options = (property, "ASC") if self.sort_options[1] == "DESC" else (property, "DESC")
            else:
                self.sort_options = (property, "ASC")

            update_header_arrows()
            self.refresh_tournaments()

        # Updates the arrow in headings when sort field changes
        def update_header_arrows():
            for field, label in header_labels.items():
                base = field
                if self.sort_options[0] == field:
                    arrow = " ▲" if self.sort_options[1] == "ASC" else " ▼"
                    label.config(text=base + arrow)
                else:
                    label.config(text=base)

        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", pady=1)
        header_labels = {}

        # function to get the arrow for a header field
        def get_arrow(field):
            if self.sort_options[0] == field:
                return " ▲" if self.sort_options[1] == "ASC" else " ▼"
            else:
                return ""
        
        # date and winner labels, binding to buttons so no button styling
        date_label = ttk.Label(header_frame, text="Date"+get_arrow("Date"), width=20, anchor="center")
        date_label.pack(side="left", padx=(0,10))
        date_label.bind("<Button-1>", lambda e: change_order("Date"))
        header_labels["Date"] = date_label

        winner_label = ttk.Label(header_frame, text="Winner"+get_arrow("Winner"), width=20, anchor="center")
        winner_label.pack(side="left")
        winner_label.bind("<Button-1>", lambda e: change_order("Winner"))
        header_labels["Winner"] = winner_label

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # scroll container
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

        update_header_arrows()
        self.refresh_tournaments()

    # opens create tournament subview
    def open_create_tournament_view(self):
        # creating subview
        win = tk.Toplevel(self)
        win.title("Create Tournament")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        # creating a group box titled date
        datepicker_frame = ttk.LabelFrame(win, text="Date")
        datepicker_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # creating the date picker
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
            foreground="black",
            selectforeground="red",
            selectbackground="blue",
            headersforeground="black",
            normalforeground="black",
            weekendforeground="black",
            othermonthforeground="gray"
        )
        cal.grid(row=0, column=1, padx=5, pady=5)

        # function to return the selected date as a string
        def chosen_date() -> str: 
            return datetime.datetime.strptime(cal.get_date(), '%m/%d/%y').strftime('%d/%m/%y')
        
        # label to show the selected date
        selected_date_label = ttk.Label(win, text=f"Selected Date: {chosen_date()}")
        selected_date_label.grid(row=1, column=1, padx=5, pady=5)

        # when selected date is changed, update the label
        def on_date_selected(event):
            selected_date_label.config(text=f"Selected Date: {chosen_date()}")

        cal.bind("<<CalendarSelected>>", on_date_selected)

        # initialising the players in the tournament as empty list
        tournament_players = []

        # group box titled current players
        current_players_frame = ttk.LabelFrame(win, text="Current Players")
        current_players_frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # scroll view
        cp_canvas = tk.Canvas(current_players_frame, borderwidth=0)
        cp_scrollbar = ttk.Scrollbar(current_players_frame, orient="vertical", command=cp_canvas.yview)
        cp_list_frame = ttk.Frame(cp_canvas)

        cp_list_frame.bind("<Configure>", lambda e: cp_canvas.configure(scrollregion=cp_canvas.bbox("all")))
        cp_canvas.create_window((0, 0), window=cp_list_frame, anchor="nw")
        cp_canvas.configure(yscrollcommand=cp_scrollbar.set)

        cp_canvas.pack(side="left", fill="both", expand=True)
        cp_scrollbar.pack(side="right", fill="y")

        # refreshing the list of players
        def refresh_current_players():
            for w in cp_list_frame.winfo_children():
                w.destroy()
            # list of players in the tournament with remove button
            for player in tournament_players:
                row = ttk.Frame(cp_list_frame)
                row.pack(fill="x", pady=1)
                ttk.Label(row, text=player[1], width=20, anchor="w").pack(side="left")
                ttk.Button(row, text="-", command=lambda p=player: remove_player(p)).pack(side="right")

        # removes the player from list, and then refreshes list
        def remove_player(player):
            tournament_players.remove(player)
            refresh_current_players()

        # group box titled add players
        add_players_frame = ttk.LabelFrame(win, text="Add Players")
        add_players_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # search query variable
        search_var = tk.StringVar()

        # text box
        search_entry = ttk.Entry(add_players_frame, textvariable=search_var)
        search_entry.pack(fill="x", padx=5, pady=5)

        # frame for search results
        results_frame = ttk.Frame(add_players_frame)
        results_frame.pack(fill="both", expand=True)

        # updating the search results
        def update_search(*args):
            for w in results_frame.winfo_children():
                w.destroy()
            if not search_var.get().strip():
                return
            results = self.controller.db.search_players(search_var.get())

            # list of all players with first and surname in query
            for player in results:
                row = ttk.Frame(results_frame)
                row.pack(fill="x", pady=1)
                ttk.Label(row, text=f"{player[1]} {player[2]}", width=20, anchor="w").pack(side="left")
                # TODO: only allow letters no numbers
                ttk.Button(row, text="+", command=lambda p=player: add_player(p)).pack(side="right")

        # adding player to tournament if they are not in it already
        def add_player(player):
            if player not in tournament_players:
                tournament_players.append(player)
            refresh_current_players()

        # updating search results when query changed
        search_var.trace_add("write", update_search)

        # group box labeled tournament type
        t_type_frame = ttk.LabelFrame(win, text="Tournament Type")
        t_type_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # tournament type section
        selected_type = tk.StringVar()
        self.build_tournament_type_section(t_type_frame, selected_type)

        # create tournament type button
        add_type_btn = ttk.Button(
            t_type_frame,
            text="+",
            command=lambda: self.open_add_type_view(t_type_frame, selected_type)
        )
        add_type_btn.pack(side="top", anchor="ne", padx=5, pady=2)

        # creates the tournament with all the data
        def create_tournament():
            new_t_id = create_uuid()
            self.controller.db.create_tournament(new_t_id, chosen_date(), len(tournament_players), selected_type.get())
            for player in tournament_players:
                self.controller.db.add_player_to_tournament(new_t_id, player[0])
            self.controller.db.create_gps_for_tournament(new_t_id, tournament_players)
            self.refresh_tournaments()
            self.open_tournament_overview(new_t_id)
            win.destroy()

        # action buttons
        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=5, column=0, pady=10)
        ttk.Button(win, text="Create", command=create_tournament).grid(row=5, column=1, pady=10)

    # opens edit tournament subview, similar to create
    def open_edit_tournament_view(self, t_id: str):
        win = tk.Toplevel(self)
        win.title("Edit Tournament")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        original_date_str = self.controller.db.read_tournament(t_id)[1]
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

        # tournament players are fetched from database
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
                # TODO: only allow letters no numbers
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

        # updating the tournament, adding new players, removing removed players
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
        ttk.Button(win, text="Update", command=update_tournament).grid(row=5, column=1, pady=10)

    # builds the list of tournament types with radio button selection 
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
    
    # create tournament type subview
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

    # refreshing tournaments list
    def refresh_tournaments(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # fetch the sorted results for the current sort
        results = self.controller.db.sort_tournaments(self.sort_options)

        for i, row in enumerate(results):
            # alternating background color for row
            bg = "#f0f0f0" if i % 2 == 0 else "#d9d9d9"

            row_frame = tk.Frame(self.results_frame, bg=bg, highlightbackground="black", highlightthickness=1)
            row_frame.pack(fill="x", pady=1)

            # displaying the date
            tk.Label(row_frame, text=row[1], width=20, anchor="center", bg=bg).pack(side="left")

            # checking if there is a winner, and then displaying it
            winner = self.controller.db.read_tournament_winner(row[0])
            if winner:
                tk.Label(row_frame, text=winner[1], width=20, anchor="center", bg=bg).pack(side="left")

            # when row or buttons clicked, open the tournament overview
            row_frame.bind("<Button-1>", lambda e, tid=row[0]: self.open_tournament_overview(tid))
            for child in row_frame.winfo_children():
                child.bind("<Button-1>", lambda e, tid=row[0]: self.open_tournament_overview(tid))

    # creates tournament overview subview
    def open_tournament_overview(self, t_id: str):
        win = tk.Toplevel(self)
        win.title("Tournament Overview")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        # functions to go to different views
        def open_brackets():
            self.open_tournament_brackets(t_id)
            win.destroy()

        def open_settings():
            self.open_edit_tournament_view(t_id)
            win.destroy()

        # fetching the tournament and player count
        t = self.controller.db.read_tournament(t_id)
        p_count = len(self.controller.db.read_tournament_players(t_id))

        # button to open brackets
        ttk.Button(win, text="Brackets", command=open_brackets).grid(row=0, column=0, columnspan=2, pady=10)

        # displaying info about the tournament
        ttk.Label(win, text="Date:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Label(win, text=t[1]).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(win, text="Player count:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Label(win, text=p_count).grid(row=2, column=1, padx=5, pady=5)

        # checking if there is a winner
        winner = self.controller.db.read_tournament_winner(t_id)
        if winner:
            # if winner then displaying the name
            ttk.Label(win, text="Winner:").grid(row=3, column=0, padx=5, pady=5)
            ttk.Label(win, text=winner[1]).grid(row=3, column=1, padx=5, pady=5)
        else:
            # if no winner then displaying other details
            eliminated_count = self.controller.db.get_players_count_eliminated(t_id)
            competing_count = 16 - eliminated_count
            ttk.Label(win, text="Round:").grid(row=3, column=0, padx=5, pady=5)
            ttk.Label(win, text=self.controller.db.get_current_round(t_id)).grid(row=3, column=1, padx=5, pady=5)
            ttk.Label(win, text="Players competing:").grid(row=4, column=0, padx=5, pady=5)
            ttk.Label(win, text=competing_count).grid(row=4, column=1, padx=5, pady=5)
            ttk.Label(win, text="Players eliminated:").grid(row=5, column=0, padx=5, pady=5)
            ttk.Label(win, text=eliminated_count).grid(row=5, column=1, padx=5, pady=5)

        # action buttons
        ttk.Button(win, text="Back", command=win.destroy).grid(row=6, column=0, pady=10)
        ttk.Button(win, text="Settings", command=open_settings).grid(row=6, column=1, pady=10)

    # building bracekts container view
    def open_tournament_brackets(self, t_id: str):
        self.bracket_win = tk.Toplevel(self)
        self.bracket_win.title("Tournament Brackets")
        self.bracket_win.grab_set()
        self.bracket_win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        # making container
        self.brackets_container = ttk.Frame(self.bracket_win)
        self.brackets_container.pack(fill="both", expand=True)

        # building brackets with specified tournament id
        self._build_brackets(t_id)

    # building actual brackets content view
    def _build_brackets(self, t_id: str):
        # removing any previous items in view
        for widget in self.brackets_container.winfo_children():
            widget.destroy()

        # getting list of all grand prixs in tournament
        # making a dictionary for the rounds
        grand_prix_list = self.controller.db.read_grand_prix(t_id)
        rounds_dict = defaultdict(list)

        # adding the gp to the dictionary ordered by round number
        for gp in grand_prix_list:
            round_num = gp[1]
            rounds_dict[round_num].append(gp)

        # sorting the round numbers then adding 999 at end
        # reversing this list and removing the 999
        # joining these to so now it creates a symmetrical list with 999 in middle
        # getting the index of item in list for 999
        round_numbers = sorted([r if r is not None else 999 for r in rounds_dict.keys()])
        rounds_reversed = sorted(round_numbers, reverse=True)[1:]
        rounds_joined = round_numbers + rounds_reversed
        final_index = rounds_joined.index(999)

        # function to make a bracket frame
        def make_frame(gp_id, round_frame):
            # reading all players in the grand prix
            gp_players = self.controller.db.read_grand_prix_players(gp_id)

            # creating a border around the frame
            match_frame = ttk.Frame(round_frame, relief="solid", borderwidth=1, padding=5)
            match_frame.pack(pady=20, fill="x")

            # creating green and black styles
            style = ttk.Style()
            style.configure("Black.TLabel", foreground="#000000")
            style.configure("Green.TLabel", foreground="#11DF11")

            # listing the players in the gp, with green font colour if they are winners
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
            
            # filling with blank lines if not all players qualified yet
            for x in range((4-len(gp_players))):
                ttk.Label(match_frame, text="", anchor="w").pack(fill="x")

            # fetching current race and player count in the gp
            current_r_count = self.controller.db.get_race_count_in_gp(gp_id)
            current_p_count = self.controller.db.get_player_count_in_gp(gp_id)

            # if not finished then button to input race results is shown
            if current_r_count < 4 and current_p_count == 4:
                ttk.Button(round_frame, text=f"Input race result {current_r_count+1}/4", command=lambda: self.open_input_race_results(gp_id, t_id)).pack(fill="x")

        # iteration over the rounds
        for col, rn in enumerate(rounds_joined):
            # title for round name
            title = f"Round {rn}" if rn != 999 else "Final"
            round_frame = ttk.LabelFrame(self.brackets_container, text=title)
            round_frame.grid(row=0, column=col, padx=40, pady=20, sticky="n")

            # building the brackets for each round
            if rn == 999: rn = None
            for gp in rounds_dict[rn]:
                if col < final_index:
                    if gp[2] == False: make_frame(gp[0], round_frame)
                elif col == final_index:
                    make_frame(gp[0], round_frame)
                else:
                    if gp[2] == True: make_frame(gp[0], round_frame)
        
        # finding the winner
        winner = self.controller.db.read_tournament_winner(t_id)
        if winner is not None:
            # if there is a winner then show the name
            # TODO: name should be a button when clicked goes to stats view with that player
            winner_label = ttk.Label(self.brackets_container, text=f"Winner: {winner[1]}", font=("Arial", 12, "bold"))
            winner_label.grid(row=1, column=len(rounds_joined)//2, pady=20)

        def go_back():
            self.open_tournament_overview(t_id)
            self.bracket_win.destroy()

        ttk.Button(self.brackets_container, text="Back", command=go_back).grid(row=2, column=0, pady=10, sticky="w")

    # refreshing the brackets after grand prix result input
    def refresh_brackets(self, t_id: str):
        self._build_brackets(t_id)
    
    # opens subview to input race results
    def open_input_race_results(self, gp_id: str, t_id: str):
        # getting the number of races data is entered for
        race_count = self.controller.db.get_race_count_in_gp(gp_id)
        win = tk.Toplevel(self)
        win.title(f"Input Race [{race_count + 1}/4] Results")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)

        # getting all the circuit names
        # mapping all the circuit names to the circuit
        circuits = self.controller.db.read_circuit_data()
        circuit_names = [c[1] for c in circuits]
        name_to_circuit = {c[1]: c for c in circuits}

        ttk.Label(win, text="Select Circuit:").grid(row=0, column=0, padx=5, pady=5)

        # drop down selection box with all circuits
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
        
        # for each player in the race, creating a result selction box 1-12
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

        # TODO: validation that all fields must be entered, and that results can't be the same
        # function to submit the results
        def insert_results():
            chosen_name = circuit_var.get()
            # finding the circuit id from its name
            if chosen_name:
                chosen_circuit = name_to_circuit[chosen_name]
                c_id = chosen_circuit[0]

            # collecting all the players
            # creating the race and adding the players and results to it
            # if this is the last race in gp then open gp results subview
            players_results = [(pid, int(var.get())) for pid, var in result_vars.items()]
            self.controller.db.create_race(gp_id, c_id, players_results)
            new_race_count = self.controller.db.get_race_count_in_gp(gp_id)
            if new_race_count == 4: self.open_input_gp_results(gp_id, t_id)
            win.destroy()
            if new_race_count < 4: self.refresh_brackets(t_id)

        # action buttons
        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=5, column=0, pady=10, sticky="w")
        ttk.Button(win, text="Insert Resuts", command=insert_results).grid(row=5, column=1, pady=10, sticky="w")

    # opens subview to input grand prix results
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

        # function to insert the grand prix results
        def save_gp_results():
            for pid, var in result_vars.items():
                if var.get():
                    self.controller.db.cursor.execute(
                        "UPDATE GrandPrixParticipation SET grandprix_result = ? WHERE grandprix_id = ? AND player_id = ?",
                        (int(var.get()), gp_id, pid)
                    )
            self.controller.db.connection.commit()
            
            # finding the top players in the gp
            top_players = self.controller.db.find_winners_for_gp(gp_id)
            new_gp_id = self.controller.db.find_next_gp_id(gp_id)

            # if this is the final bracket
            if new_gp_id == "Tournament finished":
                # finding the winner
                # setting the tournament results for the players
                winner = self.controller.db.calculate_tournament_winner(gp_id)
                #* TODO: set tournament result TournamentParticipation for all players
                self.controller.db.cursor.execute("UPDATE TournamentParticipation SET tournament_result = 1 WHERE tournament_id = ? AND player_id = ?", (t_id, winner[0]))
                self.controller.db.connection.commit()
            else:
                # otherwise add the top players to the next round
                self.controller.db.add_winners_to_gp(top_players, new_gp_id)

            win.destroy()
            self.refresh_brackets(t_id)

        ttk.Button(win, text="Complete Grand Prix", command=save_gp_results).grid(row=5, column=0, pady=10)