import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import datetime
from collections import defaultdict
from storage import create_uuid

class TournamentsPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_view()

    # this function is used to do nothing and block child window closure
    def block_window_closure(self): return

    # building the tournaments homepage with button to create tournament and list of tournaments container scrollview
    def build_view(self):
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack()
        
        # creating the title
        title_frame = ttk.Frame(self.form_frame)
        title_frame.pack(pady=(10, 5))
        ttk.Label(title_frame, text="Tournaments Dashboard", font=("TkDefaultFont", 14, "bold")).pack()
        
        # action buttons frame and button
        buttons_frame = ttk.Frame(self.form_frame)
        buttons_frame.pack(pady=(5, 10))
        create_btn = ttk.Button(buttons_frame, text="Create Tournament", command=self.open_create_tournament_view, style="UnHover.TButton", cursor="plus")
        create_btn.pack(side="left", padx=10, ipadx=10)
        self.controller.make_hoverable_btn(create_btn, "Hover", "UnHover")

        # creating the scroll container
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # the container for the tournaments list
        self.results_frame = ttk.Frame(canvas)
        self.results_frame.pack()
        canvas_window = canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.results_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        # settings the login status for all tournaments to be logged out
        self.login_status = {}
        # id: (True, "username"), ...
        results = self.controller.db.read_tournament_data()
        for res in results:
            self.login_status[res[0]] = (False, None)

        # initialising the sort options and initially loading the tournaments list
        self.sort_options = ("Date", "ASC")
        self.refresh_tournaments()

    # opens create tournament subview
    def open_create_tournament_view(self):
        # creating subview
        win = tk.Toplevel(self)
        win.title("Create Tournament")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)

        # storing the steps to create tournament as differrent views
        # settings current step index to 0
        steps = []
        current_step = tk.IntVar(value=0)

        # function to show a specific step
        # hides all steps then shows the current step
        # changes the current step index
        def show_step(index: int):
            for step in steps:
                step.pack_forget()
            steps[index].pack(padx=10, pady=10)
            steps[index+3].pack(padx=10, pady=10)
            current_step.set(index)

        # Step 1: Select date
        step1_frame = ttk.LabelFrame(win, text="Select the tournament date")
        step1 = ttk.Frame(step1_frame)

        # calculating the current date and lower and upper bounds of date range
        today = datetime.date.today()
        mindate = today - datetime.timedelta(days=365)
        maxdate = today + datetime.timedelta(days=365)

        # creating the calendar with colours for headings
        cal = Calendar(
            step1,
            selectmode="day",
            year=today.year, month=today.month, day=today.day,
            mindate=mindate, maxdate=maxdate, 
            background="#FAFAFA", foreground="black", disabledbackground="#FAFAFA",
            headersforeground="purple", selectforeground="red", normalforeground="black",
            weekendforeground="black", othermonthforeground="gray", othermonthweforeground="gray"
        )
        cal.pack(padx=10, pady=10)

        # function to get the selected date from calendar and format it correctly
        def get_date(): return datetime.datetime.strptime(cal.get_date(), "%m/%d/%y").strftime("%d/%m/%y")

        # label with selected date
        # updating label when selected date is changed
        selected_date_label = ttk.Label(step1, text=f"Selected Date: {get_date()}")
        selected_date_label.pack(pady=5)
        cal.bind("<<CalendarSelected>>", lambda e: selected_date_label.config(text=f"Selected Date: {get_date()}"))

        # frame for actions buttons
        bottom_bar = ttk.Frame(step1)
        bottom_bar.pack(fill="x", pady=(10,0))

        # cancel button closes window
        # next button shows next step
        # underlines on hover
        cancel_btn = ttk.Button(bottom_bar, text="Cancel", command=win.destroy, style="UnHover.TButton")
        cancel_btn.pack(side="left", padx=5)
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        next_btn = ttk.Button(bottom_bar, text="Next", command=lambda: show_step(1), style="UnHoverSubmit.TButton")
        next_btn.pack(side="right", padx=5)
        self.controller.make_hoverable_btn(next_btn, "HoverSubmit", "UnHoverSubmit")

        # Step 2: Select players
        step2_frame = ttk.LabelFrame(win, text="Select the tournament players")
        step2 = ttk.Frame(step2_frame)
        tournament_players = []

        # function to clear the search field when command backspace pressed
        def clear_query(event=None):
            search_field.delete(0, tk.END)

        # creating the search field
        search_frame = ttk.LabelFrame(step2, text="Search Players")
        search_frame.pack(fill="both", expand=True)
        search_var = tk.StringVar()
        vcmd = (win.register(self.controller.validate_only_letters), "%P")
        search_field = ttk.Entry(search_frame, textvariable=search_var, validate="key", validatecommand=vcmd)
        search_field.pack(fill="x", padx=5, pady=5)
        search_field.bind("<Escape>", lambda e: win.focus())
        search_field.bind("<Command-BackSpace>", clear_query)

        # search results frame
        results_outer = ttk.LabelFrame(step2, text="Add Players")
        results_outer.pack()

        # creating the search results scrollview container
        results_canvas = tk.Canvas(results_outer, height=150, width=250, bg="#F7F7F7", highlightthickness=0)
        results_scrollbar = ttk.Scrollbar(results_outer, orient="vertical", command=results_canvas.yview)
        results_canvas.configure(yscrollcommand=results_scrollbar.set)
        results_canvas.pack(side="left", fill="both")
        results_scrollbar.pack(side="right", fill="y")
        results_frame = ttk.Frame(results_canvas)
        results_canvas.create_window((0, 0), window=results_frame, anchor="nw")

        def on_frame_configure1(event):
            results_canvas.configure(scrollregion=results_canvas.bbox("all"))
        results_frame.bind("<Configure>", on_frame_configure1)

        def on_canvas_configure1(event):
            results_canvas.itemconfig("all", width=event.width)
        results_canvas.bind("<Configure>", on_canvas_configure1)

        # current players frame
        current_players_outer = ttk.LabelFrame(step2, text="Current Players")
        current_players_outer.pack()

        # creating the current players scrollview container
        current_players_canvas = tk.Canvas(current_players_outer, height=150, width=250, bg="#F7F7F7", highlightthickness=0)
        current_players_scrollbar = ttk.Scrollbar(current_players_outer, orient="vertical", command=current_players_canvas.yview)
        current_players_canvas.configure(yscrollcommand=current_players_scrollbar.set)
        current_players_canvas.pack(side="left", fill="both")
        current_players_scrollbar.pack(side="right", fill="y")
        current_players_frame = ttk.Frame(current_players_canvas)
        current_players_canvas.create_window((0, 0), window=current_players_frame, anchor="nw")

        def on_frame_configure2(event):
            current_players_canvas.configure(scrollregion=current_players_canvas.bbox("all"))
        current_players_frame.bind("<Configure>", on_frame_configure2)

        def on_canvas_configure2(event):
            current_players_canvas.itemconfig("all", width=event.width)
        current_players_canvas.bind("<Configure>", on_canvas_configure2)
        
        # function to update the search results
        def update_search_results(*args):
            # deleting previous results
            for w in results_frame.winfo_children(): w.destroy()
            query = search_var.get().strip()

            # if no query then hide scrollbar
            if not query:
                results_canvas.yview_moveto(0)
                results_canvas.configure(scrollregion=(0, 0, 0, 0))
                return
            
            # fetching results and only showing players not already selected
            results = self.controller.db.search_players(query)
            results = [r for r in results if r not in tournament_players]

            # creating the row with player name
            # adding special padding for first and last results
            for i, player in enumerate(results):
                if i == 0: pdy = (4,0)
                elif i == len(results)-1: pdy = (0,10)
                else: pdy = (0,0)
                row = ttk.Frame(results_frame)
                row.pack(fill="x", padx=10, pady=pdy)
                ttk.Label(row, text=f"{player[1]} {player[2]}").pack(side="left")
                ttk.Button(row, text="+", command=lambda p=player: add_player(p)).pack(side="right")

        # function to update current players list when player is added or removed
        def refresh_current_players():
            for w in current_players_frame.winfo_children(): w.destroy()
            for i, player in enumerate(tournament_players):
                if i == 0: pdy = (4,0)
                elif i == len(tournament_players)-1: pdy = (0,10)
                else: pdy = (0,0)
                row = ttk.Frame(current_players_frame)
                row.pack(fill="x", padx=10, pady=pdy)
                ttk.Label(row, text=f"{player[1]} {player[2]}").pack(side="left")
                ttk.Button(row, text="-", command=lambda p=player: remove_player(p)).pack(side="right")

        # function to remove player from tournament
        # remove from database then refresh views
        def remove_player(p: tuple[str, str, str, int]):
            tournament_players.remove(p)
            refresh_current_players()
            update_search_results()

        # function to add player to tournament
        # add to database then refresh views
        def add_player(p: tuple[str, str, str, int]):
            if p not in tournament_players:
                tournament_players.append(p)
            refresh_current_players()
            update_search_results()

        search_var.trace_add("write", update_search_results)

        #* Temporary function
        # function to validate the correct number of players are added
        # if correct then show the next step
        def validate_player_count():
            if len(tournament_players) == 16:
                show_step(2)
            else:
                messagebox.showerror("Incorrect number of players", f"Number of players should be 16.\nCurrently {len(tournament_players)} players added.")

        bottom_bar = ttk.Frame(step2)
        bottom_bar.pack(fill="x", pady=(10,0))

        back_btn = ttk.Button(bottom_bar, text="Back", command=lambda: show_step(0), style="UnHover.TButton")
        back_btn.pack(side="left", padx=5)
        self.controller.make_hoverable_btn(back_btn, "Hover", "UnHover")

        next_btn = ttk.Button(bottom_bar, text="Next", command=validate_player_count, style="UnHoverSubmit.TButton")
        next_btn.pack(side="right", padx=5)
        self.controller.make_hoverable_btn(next_btn, "HoverSubmit", "UnHoverSubmit")

        cancel_btn = ttk.Button(bottom_bar, text="Cancel", command=win.destroy, style="UnHover.TButton")
        cancel_btn.pack(padx=5)
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        # Step 3: Select tournament type
        step3_frame = ttk.LabelFrame(win, text="Select the tournament type")
        step3 = ttk.Frame(step3_frame)
        selected_type = tk.StringVar()

        types_container = ttk.Frame(step3)
        types_container.pack(fill="x")
        
        self.build_tournament_type_section(types_container, selected_type)
        ttk.Button(step3, text="+", command=lambda: self.open_add_type_view(types_container, selected_type), style="UnHover.TButton", cursor="plus").pack(anchor="ne", padx=5, pady=2)

        # Create the tournament
        def create_tournament():
            # validation that the tournament type isn't empty
            ttype = selected_type.get()
            if ttype == "":
                messagebox.showerror("Missing Info", "Please select a tournament type.")
                return
            
            # creating tournament with data, making new id
            new_t_id = create_uuid()
            self.controller.db.create_tournament(new_t_id, get_date(), len(tournament_players), ttype)

            # adding all players to tournament in TournamentParticipation table
            for player in tournament_players:
                self.controller.db.add_player_to_tournament(new_t_id, player[0])

            # creating grand prixs and adding players to them in GrandPrixParticipation table
            self.controller.db.create_gps_for_tournament(new_t_id, tournament_players)

            # refreshing tournaments list to account for the new tournament
            # Adding the new tournament to login status dictionary
            # opening create account view for user to make an account
            self.refresh_tournaments()
            self.login_status[new_t_id] = (False, None)
            self.open_create_account(new_t_id)
            win.destroy()

        bottom_bar = ttk.Frame(step3)
        bottom_bar.pack(fill="x", pady=(10,0))

        back_btn = ttk.Button(bottom_bar, text="Back", command=lambda: show_step(1), style="UnHover.TButton")
        back_btn.pack(side="left", padx=5)
        self.controller.make_hoverable_btn(back_btn, "Hover", "UnHover")

        create_btn = ttk.Button(bottom_bar, text="Create", command=create_tournament, style="UnHoverSubmit.TButton")
        create_btn.pack(side="right", padx=5)
        self.controller.make_hoverable_btn(create_btn, "HoverSubmit", "UnHoverSubmit")

        cancel_btn = ttk.Button(bottom_bar, text="Cancel", command=win.destroy, style="UnHover.TButton")
        cancel_btn.pack(padx=5)
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        # adding the frames to the steps view array and then showing step 1
        steps.extend([step1, step2, step3, step1_frame, step2_frame, step3_frame])
        show_step(0)

    # opens edit tournament subview, similar to create
    def open_edit_tournament_view(self, t_id: str):
        # creating subview
        win = tk.Toplevel(self)
        win.title("Edit Tournament")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)

        # function to go back to tournament overview
        def go_back():
            self.open_tournament_overview(t_id)
            win.destroy()

        # storing the steps to create tournament as differrent views
        # settings current step index to 0
        steps = []
        current_step = tk.IntVar(value=0)

        # function to show a specific step
        # hides all steps then shows the current step
        # changes the current step index
        def show_step(index: int):
            for step in steps:
                step.pack_forget()
            steps[index].pack(padx=10, pady=10)
            steps[index+4].pack(padx=10, pady=10)
            current_step.set(index)
        
        # Step 1: Select date
        step1_frame = ttk.LabelFrame(win, text="Select the tournament date")
        step1 = ttk.Frame(step1_frame)

        # calculating the current date and lower and upper bounds of date range
        # date range is within 1 year of original date
        original_date_str = self.controller.db.read_tournament(t_id)[1]
        original_date = datetime.datetime.strptime(original_date_str, "%d/%m/%y").date()
        mindate = original_date - datetime.timedelta(days=365)
        maxdate = original_date + datetime.timedelta(days=365)

        # creating the calendar with colours for headings
        cal = Calendar(
            step1,
            selectmode="day",
            year=original_date.year, month=original_date.month, day=original_date.day,
            mindate=mindate, maxdate=maxdate, 
            background="#FAFAFA", foreground="black", disabledbackground="#FAFAFA",
            headersforeground="purple", selectforeground="red", normalforeground="black",
            weekendforeground="black", othermonthforeground="gray", othermonthweforeground="gray"
        )
        cal.pack(padx=10, pady=10)

        # function to get the selected date from calendar and format it correctly
        def get_date(): return datetime.datetime.strptime(cal.get_date(), "%m/%d/%y").strftime("%d/%m/%y")

        # label with selected date
        # updating label when selected date is changed
        selected_date_label = ttk.Label(step1, text=f"Selected Date: {get_date()}")
        selected_date_label.pack(pady=5)
        cal.bind("<<CalendarSelected>>", lambda e: selected_date_label.config(text=f"Selected Date: {get_date()}"))

        # frame for actions buttons
        bottom_bar = ttk.Frame(step1)
        bottom_bar.pack(fill="x", pady=(10,0))

        # cancel button closes window
        # next button shows next step
        # underlines on hover
        cancel_btn = ttk.Button(bottom_bar, text="Cancel", command=go_back, style="UnHover.TButton")
        cancel_btn.pack(side="left", padx=5)
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        next_btn = ttk.Button(bottom_bar, text="Next", command=lambda: show_step(1), style="UnHoverSubmit.TButton")
        next_btn.pack(side="right", padx=5)
        self.controller.make_hoverable_btn(next_btn, "HoverSubmit", "UnHoverSubmit")

        # Step 2: Select players
        step2_frame = ttk.LabelFrame(win, text="Select the tournament players")
        step2 = ttk.Frame(step2_frame)

        # tournament players are fetched from database
        tournament_players = self.controller.db.read_tournament_players(t_id)
        removed_players = []
        added_players = []

        # function to clear the search field when command backspace pressed
        def clear_query(event=None):
            search_field.delete(0, tk.END)

        # creating the search field
        search_frame = ttk.LabelFrame(step2, text="Search Players")
        search_frame.pack(fill="both", expand=True)
        search_var = tk.StringVar()
        vcmd = (win.register(self.controller.validate_only_letters), "%P")
        search_field = ttk.Entry(search_frame, textvariable=search_var, validate="key", validatecommand=vcmd)
        search_field.pack(fill="x", padx=5, pady=5)
        search_field.bind("<Escape>", lambda e: win.focus())
        search_field.bind("<Command-BackSpace>", clear_query)

        # search results frame
        results_outer = ttk.LabelFrame(step2, text="Add Players")
        results_outer.pack()

        # creating the search results scrollview container
        results_canvas = tk.Canvas(results_outer, height=150, width=250, bg="#F7F7F7", highlightthickness=0)
        results_scrollbar = ttk.Scrollbar(results_outer, orient="vertical", command=results_canvas.yview)
        results_canvas.configure(yscrollcommand=results_scrollbar.set)
        results_canvas.pack(side="left", fill="both")
        results_scrollbar.pack(side="right", fill="y")
        results_frame = ttk.Frame(results_canvas)
        results_canvas.create_window((0, 0), window=results_frame, anchor="nw")

        def on_frame_configure1(event):
            results_canvas.configure(scrollregion=results_canvas.bbox("all"))
        results_frame.bind("<Configure>", on_frame_configure1)

        def on_canvas_configure1(event):
            results_canvas.itemconfig("all", width=event.width)
        results_canvas.bind("<Configure>", on_canvas_configure1)

        # current players frame
        current_players_outer = ttk.LabelFrame(step2, text="Current Players")
        current_players_outer.pack()

        # creating the current players scrollview container
        current_players_canvas = tk.Canvas(current_players_outer, height=150, width=250, bg="#F7F7F7", highlightthickness=0)
        current_players_scrollbar = ttk.Scrollbar(current_players_outer, orient="vertical", command=current_players_canvas.yview)
        current_players_canvas.configure(yscrollcommand=current_players_scrollbar.set)
        current_players_canvas.pack(side="left", fill="both")
        current_players_scrollbar.pack(side="right", fill="y")
        current_players_frame = ttk.Frame(current_players_canvas)
        current_players_canvas.create_window((0, 0), window=current_players_frame, anchor="nw")

        def on_frame_configure2(event):
            current_players_canvas.configure(scrollregion=current_players_canvas.bbox("all"))
        current_players_frame.bind("<Configure>", on_frame_configure2)

        def on_canvas_configure2(event):
            current_players_canvas.itemconfig("all", width=event.width)
        current_players_canvas.bind("<Configure>", on_canvas_configure2)

        # function to update the search results
        def update_search_results(*args):
            for w in results_frame.winfo_children(): w.destroy()
            query = search_var.get().strip()

            # if no query then hide scrollbar
            if not query:
                results_canvas.yview_moveto(0)
                results_canvas.configure(scrollregion=(0, 0, 0, 0))
                return
            
            # fetching results and only showing players not already selected
            results = self.controller.db.search_players(query)
            results = [r for r in results if r not in tournament_players]

            # creating the row with player name
            # adding special padding for first and last results
            for i, player in enumerate(results):
                if i == 0: pdy = (4,0)
                elif i == len(results)-1: pdy = (0,10)
                else: pdy = (0,0)
                row = ttk.Frame(results_frame)
                row.pack(fill="x", padx=10, pady=pdy)
                ttk.Label(row, text=f"{player[1]} {player[2]}").pack(side="left")
                #* Temporarily disabled
                ttk.Button(row, text="+", command=lambda p=player: add_player(p), state="disabled").pack(side="right")

        # function to update current players list when player is added or removed
        def refresh_current_players():
            for w in current_players_frame.winfo_children(): w.destroy()
            for i, player in enumerate(tournament_players):
                if i == 0: pdy = (4,0)
                elif i == len(tournament_players)-1: pdy = (0,10)
                else: pdy = (0,0)
                row = ttk.Frame(current_players_frame)
                row.pack(fill="x", padx=10, pady=pdy)
                ttk.Label(row, text=f"{player[1]} {player[2]}").pack(side="left")
                #* Temporarily disabled
                ttk.Button(row, text="-", command=lambda p=player: remove_player(p), state="disabled").pack(side="right")

        # function to remove player from tournament
        # remove from database then refresh views
        def remove_player(p: tuple[str, str, str, int]):
            tournament_players.remove(p)
            removed_players.append(p[0])
            refresh_current_players()
            update_search_results()

        # function to add player to tournament
        # add to database then refresh views
        def add_player(p: tuple[str, str, str, int]):
            if p not in tournament_players:
                tournament_players.append(p)
                added_players.append(p[0])
            refresh_current_players()
            update_search_results()

        refresh_current_players()

        search_var.trace_add("write", update_search_results)

        #* Temporary function
        # function to validate the correct number of players are added
        # if correct then show the next step
        def validate_player_count():
            if len(tournament_players) == 16:
                show_step(2)
            else:
                messagebox.showerror("Incorrect number of players", f"Number of players should be 16.\nCurrently {len(tournament_players)} players added.")

        bottom_bar = ttk.Frame(step2)
        bottom_bar.pack(fill="x", pady=(10,0))

        back_btn = ttk.Button(bottom_bar, text="Back", command=lambda: show_step(0), style="UnHover.TButton")
        back_btn.pack(side="left", padx=5)
        self.controller.make_hoverable_btn(back_btn, "Hover", "UnHover")

        next_btn = ttk.Button(bottom_bar, text="Next", command=validate_player_count, style="UnHoverSubmit.TButton")
        next_btn.pack(side="right", padx=5)
        self.controller.make_hoverable_btn(next_btn, "HoverSubmit", "UnHoverSubmit")

        cancel_btn = ttk.Button(bottom_bar, text="Cancel", command=go_back, style="UnHover.TButton")
        cancel_btn.pack(padx=5)
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        # Step 3: Select tournament type
        step3_frame = ttk.LabelFrame(win, text="Select the tournament type")
        step3 = ttk.Frame(step3_frame)
        selected_type = tk.StringVar()
        current_type_id = self.controller.db.read_tournament_type(t_id)

        types_container = ttk.Frame(step3)
        types_container.pack(fill="x")

        # function to check if user has selected a tournament type, if they have then show the next step otherwise show an error
        def validate_ttype():
            ttype = selected_type.get()
            if ttype == "":
                messagebox.showerror("Missing Info", "Please select a tournament type.")
                return
            else:
                show_step(3)
        
        # building the tournament type list and the add button
        self.build_tournament_type_section(types_container, selected_type, current_type_id)
        ttk.Button(step3, text="+", command=lambda: self.open_add_type_view(types_container, selected_type), style="UnHover.TButton", cursor="plus").pack(anchor="ne", padx=5, pady=2)

        # making frame for the actions buttons
        bottom_bar = ttk.Frame(step3)
        bottom_bar.pack(fill="x", pady=(10,0))

        # back button that shows the previous step
        back_btn = ttk.Button(bottom_bar, text="Back", command=lambda: show_step(1), style="UnHover.TButton")
        back_btn.pack(side="left", padx=5)
        self.controller.make_hoverable_btn(back_btn, "Hover", "UnHover")

        # next button that validates and shows the next step
        next_btn = ttk.Button(bottom_bar, text="Next", command=validate_ttype, style="UnHoverSubmit.TButton")
        next_btn.pack(side="right", padx=5)
        self.controller.make_hoverable_btn(next_btn, "HoverSubmit", "UnHoverSubmit")

        # cancel button which closes the create view
        cancel_btn = ttk.Button(bottom_bar, text="Cancel", command=go_back, style="UnHover.TButton")
        cancel_btn.pack(padx=5)
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        # Step 4: Manage accounts
        step4_frame = ttk.LabelFrame(win, text="Manage accounts")
        step4 = ttk.Frame(step4_frame)

        # creating container for the accounts list and building it
        accounts_container = ttk.Frame(step4)
        accounts_container.pack(fill="x")
        self.build_accounts_section(t_id, accounts_container)

        # Update the tournament
        def update_tournament():
            # updating the tournament with data
            self.controller.db.update_tournament(t_id, get_date(), len(tournament_players), selected_type.get())

            # adding new players, removing old players
            original_players = [p[0] for p in self.controller.db.read_tournament_players(t_id)]
            for player in added_players:
                if player not in original_players:
                    self.controller.db.add_player_to_tournament(t_id, player)                
            for player in removed_players:
                if player in original_players:
                    self.controller.db.remove_player_from_tournament(t_id, player)

            # going back to tournament overview and refreshing tournaments list
            self.refresh_tournaments()
            go_back()

        # bottom bar frame for action buttons
        bottom_bar = ttk.Frame(step4)
        bottom_bar.pack(fill="x", pady=(10,0))

        # back button
        back_btn = ttk.Button(bottom_bar, text="Back", command=lambda: show_step(2), style="UnHover.TButton")
        back_btn.pack(side="left", padx=5)
        self.controller.make_hoverable_btn(back_btn, "Hover", "UnHover")

        # update button
        update_btn = ttk.Button(bottom_bar, text="Update", command=update_tournament, style="UnHoverSubmit.TButton")
        update_btn.pack(side="right", padx=5)
        self.controller.make_hoverable_btn(update_btn, "HoverSubmit", "UnHoverSubmit")

        # cancel button
        cancel_btn = ttk.Button(bottom_bar, text="Cancel", command=go_back, style="UnHover.TButton")
        cancel_btn.pack(padx=5)
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        # adding the frames to the steps view array and then showing step 1
        steps.extend([step1, step2, step3, step4, step1_frame, step2_frame, step3_frame, step4_frame])
        show_step(0)

    # builds the list of tournament types with radio button selection 
    def build_tournament_type_section(self, parent: ttk.Frame, selected_type: tk.StringVar, current_type_id: str | None = None):
        for widget in parent.winfo_children():
            widget.destroy()

        types = self.controller.db.read_tournament_types()
        for t in types:
            desc = f"{t[1]} cont, {t[2]} GPs, {"Long" if t[3] else "Normal"}"
            rb = ttk.Radiobutton(parent, text=desc, value=t[0], variable=selected_type)
            rb.pack(anchor="w")

            if current_type_id:
                selected_type.set(current_type_id)
    
    # create tournament type subview
    def open_add_type_view(self, parent_frame: ttk.Frame, selected_type: tk.StringVar):
        win = tk.Toplevel(self)
        win.title("Add Tournament Type")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)

        ttk.Label(win, text="Default Continuers:").grid(row=0, column=0, padx=5, pady=5)
        cont_entry = ttk.Entry(win)
        cont_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(win, text="Number of Grand Prix:").grid(row=1, column=0, padx=5, pady=5)
        gp_entry = ttk.Entry(win)
        gp_entry.grid(row=1, column=1, padx=5, pady=5)

        longer_var = tk.BooleanVar()
        ttk.Checkbutton(win, text="Longer Style", variable=longer_var).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        def save_type():
            self.controller.db.create_tournament_type(
                int(cont_entry.get()),
                int(gp_entry.get()),
                longer_var.get()
            )
            win.destroy()
            self.build_tournament_type_section(parent_frame, selected_type)

        ttk.Button(win, text="Cancel", command=win.destroy).grid(row=3, column=0, pady=10)
        ttk.Button(win, text="Save", command=save_type).grid(row=3, column=1, pady=10)

    # builds the list of accounts for tournament creator/editor
    def build_accounts_section(self, t_id: str, parent: ttk.Frame, delete_mode=False):
        # deleting previous text
        for widget in parent.winfo_children():
            widget.destroy()
        
        # function to confirm user intends to delete the accounts
        def confirm_delete(account_id: str, username: str):
            # showing the message box
            confirm = messagebox.askyesno("Delete Account", f"Are you sure you want to delete the account for '{username}'?")
            if confirm:
                # if they say yes then delete the account
                self.controller.db.delete_account(account_id)
                # if the user deleted the account which was logged in then log them out
                if username == self.login_status[t_id][1]:
                    self.login_status[t_id] = (False, None)
                # if there were 2 accounts and so there is only 1 now, then rebuild with delete_mode off to disable deleting
                if len(accounts) == 2:
                    self.build_accounts_section(t_id, parent, delete_mode=False)
                else:
                    # otherwise if more than 1 account then leave delete mode on in case user wants to delete another
                    self.build_accounts_section(t_id, parent, delete_mode=True)

        # frame for the title
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 5))
        ttk.Label(header_frame, text="Username", font=("TkDefaultFont", 10, "bold")).pack(anchor="w", padx=10)

        # getting list of all accounts in the tournament
        accounts = self.controller.db.read_tournament_accounts(t_id)

        # for every account
        for a in accounts:
            # getting the account id and username from subscript
            account_id = a[0]
            username = a[2]

            # if delete mode is on then text color should be red and underlined
            if delete_mode:
                # binding button to show confirmation
                lbl = ttk.Label(parent, text=username, font=("TkDefaultFont", 10, "underline"), foreground="#df3832", cursor="hand2")
                lbl.bind("<Button-1>", lambda e, a_id=account_id, u=username: confirm_delete(a_id, u))
            else:
                # otherwise listing the username
                lbl = ttk.Label(parent, text=username, font=("TkDefaultFont", 10))
            lbl.pack(anchor="w", padx=20, pady=2)
        
        # frame for action buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=(10, 5))

        # settings the button title and styling if in delete mode or not
        minus_style = "HoverDelete.TButton" if delete_mode else "UnHover.TButton"
        minus_text = "Done" if delete_mode else "-"
        
        # if more than 1 account then the edit button is shown to allow user to delete accounts
        if len(accounts) > 1:
            minus_btn = ttk.Button(btn_frame, text=minus_text, command=lambda: self.build_accounts_section(t_id, parent, not delete_mode), style=minus_style, cursor="pirate")
            minus_btn.pack(side="left", padx=5)

        # if not in edit mode then show the add button to create an account
        if not delete_mode:
            add_btn = ttk.Button(btn_frame, text="+", command=lambda: self.open_create_account(t_id, parent), style="UnHover.TButton", cursor="plus")
            add_btn.pack(side="right", padx=5)

    # function to open the create account view
    def open_create_account(self, t_id: str, parent_frame: ttk.Frame | None = None):
        # creating a small pop up window for data entry
        # blocking action on other windows, and blocking window closure using red x
        win = tk.Toplevel(self)
        win.title("Create Account")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)

        # registering the username validation for only letters and numbers
        vcmd_username = (win.register(self.controller.validate_only_letters_numbers), "%P")

        # functions to clear the textfield when command backspace pressed
        def clear_uname(event=None):
            uname.delete(0, tk.END)
        def clear_pword(event=None):
            pword1.delete(0, tk.END)
        def clear_pword2(event=None):
            pword2.delete(0, tk.END)

        # text box for username
        # adding validation on every key press to only allow numbers and letters to be typed
        # binding escape to deselect field
        ttk.Label(win, text="Username:").grid(row=0, column=0, padx=(30,10), pady=(16,8), sticky="e")
        uname = ttk.Entry(win, validate="key", validatecommand=vcmd_username)
        uname.grid(row=0, column=1, padx=(5,30), pady=(16,8))
        uname.bind("<Escape>", lambda e: win.focus())
        uname.bind("<Command-BackSpace>", clear_uname)

        # text box for password
        ttk.Label(win, text="Password:").grid(row=1, column=0, padx=(30,10), pady=8, sticky="e")
        pword1 = ttk.Entry(win)
        pword1.grid(row=1, column=1, padx=(5,30), pady=8)
        pword1.bind("<Escape>", lambda e: win.focus())
        pword1.bind("<Command-BackSpace>", clear_pword)

        # text box to reenter password (double erntry validation)
        ttk.Label(win, text="Reenter Password:").grid(row=2, column=0, padx=(30,10), pady=8, sticky="e")
        pword2 = ttk.Entry(win)
        pword2.grid(row=2, column=1, padx=(5,30), pady=8)
        pword2.bind("<Escape>", lambda e: win.focus())
        pword2.bind("<Command-BackSpace>", clear_pword2)

        # function to add account and close window
        def create_password():
            # fetching the data
            username = uname.get()
            password1 = pword1.get()
            password2 = pword2.get()
            # if passwords don't match then show error
            if password1 != password2:
                messagebox.showerror("Passwords don't match", "Please ensure you have typed both passwords correctly")
                return
            # if data is empty then show error
            if username == "" or password1 == "" or password2 == "":
                messagebox.showerror("Fill out all fields", "Please fill out all fields.")
                return
            # if password length incorrect then show error
            if len(password1) < 10:
                messagebox.showerror("Password not long enough", "Please make the password at least 10 characters.")
                return
            
            # trying to add account to database
            # username must be unique to the tournament
            successful = self.controller.db.create_account(t_id, username, password1)
            if successful:
                # if addition was successful then close window
                win.destroy()
                if parent_frame:
                    # if this window was opened from tournament settings then rebuild the accounts list
                    self.build_accounts_section(t_id, parent_frame)
                else:
                    # if window opened acter tournament creating then log them in and open tournament overview
                    self.login_status[t_id] = (True, username)
                    self.open_tournament_overview(t_id)
            else:
                # if username not unique then show error
                messagebox.showerror("Username already taken.", "Please ensure the username is unique for this tournament.")
                return

        # buttons to cancel or create account
        # cancel closes this window, and create runs the above function
        # when hovers over, the text is underlined
        cancel_btn = ttk.Button(win, text="Cancel", command=win.destroy, style="UnHover.TButton", cursor="mouse")
        cancel_btn.grid(row=3, column=0, padx=(30,0), pady=(10,16), ipadx=10, sticky="w")
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        create_btn = ttk.Button(win, text="Create", command=create_password, style="UnHoverSubmit.TButton", cursor="mouse")
        create_btn.grid(row=3, column=1, padx=(0,30), pady=(10,16), ipadx=10, sticky="e")
        self.controller.make_hoverable_btn(create_btn, "HoverSubmit", "UnHoverSubmit")

    # function to open the login view for a tournament
    def open_login_view(self, t_id: str):
        # creating a small pop up window for data entry
        # blocking action on other windows, and blocking window closure using red x
        win = tk.Toplevel(self)
        win.title("Login Account")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)

        # registering the validation for username, only letters and numbers
        vcmd_username = (win.register(self.controller.validate_only_letters_numbers), "%P")

        # functions to clear the textfield when command backspace pressed
        def clear_uname(event=None):
            uname.delete(0, tk.END)
        def clear_pword(event=None):
            pword.delete(0, tk.END)

        # text box for username
        ttk.Label(win, text="Username:").grid(row=0, column=0, padx=(0,10), pady=(16,8), sticky="e")
        uname = ttk.Entry(win, validate="key", validatecommand=vcmd_username)
        uname.grid(row=0, column=1, padx=(5,20), pady=(16,8))
        uname.bind("<Escape>", lambda e: win.focus())
        uname.bind("<Command-BackSpace>", clear_uname)

        # text box for password
        ttk.Label(win, text="Password:").grid(row=1, column=0, padx=(0,10), pady=8, sticky="e")
        pword = ttk.Entry(win, show="")
        pword.grid(row=1, column=1, padx=(5,20), pady=8)
        pword.bind("<Escape>", lambda e: win.focus())
        pword.bind("<Command-BackSpace>", clear_pword)

        # check mark box to toggle showing the raw password or ***
        # storing the value as integer
        check_selection = tk.IntVar(value=1)
        # function to toggle showing raw password or *** when check state changed
        def toggle_pwd():
            if check_selection.get() == 1:
                pword.config(show="")
            else:
                pword.config(show="*")
        # storing value to the variable above, when check selected variable is 1, when deselected variable is 0
        checkbutton = tk.Checkbutton(win, text="Show Password", variable=check_selection, onvalue=1, offvalue=0, command=toggle_pwd)
        checkbutton.grid(row=2, column=1)

        # attempting to log the user in
        def login(event=None):
            # fetching data
            username = uname.get()
            password = pword.get()
            # trying to log the user in
            successful = self.controller.db.attempt_login(t_id, username, password)
            if successful:
                # if login successful then change dictionary value to show user is logged in, and reopen tournament overview
                win.destroy()
                self.login_status[t_id] = (True, username)
                self.t_overview_win.destroy()
                self.open_tournament_overview(t_id)
            else:
                # if login fails then show error
                messagebox.showerror("Login unsuccessful.", "Incorrect username or password")
                return
        
        # allowing user to click return button to simulate login button press
        win.bind("<Return>", login)

        # buttons to cancel or login
        # cancel closes this window, and login runs the above function
        # when hovers over, the text is underlined
        cancel_btn = ttk.Button(win, text="Cancel", command=win.destroy, style="UnHover.TButton", cursor="mouse")
        cancel_btn.grid(row=3, column=0, padx=(20,0), pady=(10,16), ipadx=10, sticky="e")
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        login_btn = ttk.Button(win, text="Login", command=login, style="UnHoverSubmit.TButton", cursor="mouse")
        login_btn.grid(row=3, column=1, padx=(0,20), pady=(10,16), ipadx=10, sticky="e")
        self.controller.make_hoverable_btn(login_btn, "HoverSubmit", "UnHoverSubmit")

    # refreshing tournaments list
    def refresh_tournaments(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

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

        # function to get the arrow for a header field
        def get_arrow(field: str):
            if self.sort_options[0] == field:
                return " ▲" if self.sort_options[1] == "ASC" else " ▼"
            else:
                return ""
            
        header_labels = {}
        
        # date and winner labels, they are lickable buttons with underline on hover, next to the title is the arrow showing sort order
        date_label = ttk.Label(self.results_frame, text="Date"+get_arrow("Date"), width=32, anchor="center")
        date_label.grid(row=0, column=0, padx=0, pady=2)
        date_label.bind("<Button-1>", lambda e: change_order("Date"))
        header_labels["Date"] = date_label
        self.controller.make_hoverable(date_label)

        winner_label = ttk.Label(self.results_frame, text="Winner"+get_arrow("Winner"), width=32, anchor="center")
        winner_label.grid(row=0, column=1, padx=0, pady=2)
        winner_label.bind("<Button-1>", lambda e: change_order("Winner"))
        header_labels["Winner"] = winner_label
        self.controller.make_hoverable(winner_label)

        # initially showing the correct arrows
        update_header_arrows()

        # fetching the tournaments data
        results = self.controller.db.sort_tournaments(self.sort_options)

        if len(results) == 0:
            ttk.Label(self.results_frame, text="You haven't created any tournaments yet.\nClick the create button above!").grid(row=1, column=0, columnspan=2)
            return

        # iterating over all results with start index 1 to account for header row
        for i, row in enumerate(results, start=1):
            # alternating background colour for row
            bg = "#f0f0f0" if i % 2 == 0 else "#d9d9d9"

            # Date column
            date_label = tk.Label(self.results_frame, text=row[1], width=32, anchor="center", bg=bg, pady=4)
            date_label.grid(row=i, column=0, pady=2)

            # Winner column
            # fetching winner and displaying name otherwise dash if no winner
            winner = self.controller.db.read_tournament_winner(row[0])
            winner_text = winner[1] if winner else "—"
            winner_label = tk.Label(self.results_frame, text=winner_text, width=32, anchor="center", bg=bg, pady=4)
            winner_label.grid(row=i, column=1, pady=2)

            # clicking any column opens tournament overview
            date_label.bind("<Button-1>", lambda e, t_id=row[0]: self.open_tournament_overview(t_id))
            winner_label.bind("<Button-1>", lambda e, t_id=row[0]: self.open_tournament_overview(t_id))

    # creates tournament overview subview
    def open_tournament_overview(self, t_id: str):
        # applying self.t_overview_win as alternative name to win so view can be closed from another function: when user login or logout
        self.t_overview_win = win = tk.Toplevel(self)
        win.title("Tournament Overview")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)

        # function to open brackets
        def open_brackets(login_data: tuple[bool, str | None]):
            self.open_tournament_brackets(t_id, login_data)
            win.destroy()

        # function to open settings
        def open_settings():
            self.open_edit_tournament_view(t_id)
            win.destroy()

        # fetching the tournament and player count
        t = self.controller.db.read_tournament(t_id)
        p_count = len(self.controller.db.read_tournament_players(t_id))

        # function to logout
        def logout():
            # set status to logged out and then reopen tournament overview
            self.login_status[t_id] = (False, None)
            win.destroy()
            self.open_tournament_overview(t_id)

        # storing internally
        login_status = self.login_status[t_id]
        # if user is logged in
        if login_status[0]:
            # text showing who is logged in
            # button for user to logout
            ttk.Label(win, text=f"Logged in as {login_status[1]}").grid(row=0, column=0, columnspan=2, padx=10, pady=8)
            logout_btn = ttk.Button(win, text="Logout", command=logout, cursor="pirate", style="UnHover.TButton")
            logout_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=8, ipadx=20)
            self.controller.make_hoverable_btn(logout_btn, "Hover", "UnHover")
        else:
            # if user is logged out then show button to login
            login_btn = ttk.Button(win, text="Login", command=lambda: self.open_login_view(t_id), cursor="spraycan", style="UnHover.TButton")
            login_btn.grid(row=0, column=0, columnspan=2, padx=10, pady=8, ipadx=20)
            self.controller.make_hoverable_btn(login_btn, "Hover", "UnHover")

        # button to open brackets
        brackets_btn = ttk.Button(win, text="Brackets", command=lambda: open_brackets(login_status), style="UnHoverSubmit.TButton", cursor="mouse")
        brackets_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=8, ipadx=20)
        self.controller.make_hoverable_btn(brackets_btn, "HoverSubmit", "UnHoverSubmit")

        # displaying info about the tournament
        ttk.Label(win, text="Date:").grid(row=3, column=0, padx=(20,10), pady=8, sticky="e")
        ttk.Label(win, text=t[1]).grid(row=3, column=1, padx=(5,10), pady=8, sticky="w")

        ttk.Label(win, text="Player count:").grid(row=4, column=0, padx=(20,10), pady=8, sticky="e")
        ttk.Label(win, text=p_count).grid(row=4, column=1, padx=(5,10), pady=8, sticky="w")

        # checking if there is a winner
        winner = self.controller.db.read_tournament_winner(t_id)
        if winner:
            # if winner then displaying the name
            ttk.Label(win, text="Winner:").grid(row=5, column=0, padx=(20,10), pady=8, sticky="e")
            ttk.Label(win, text=winner[1]).grid(row=5, column=1, padx=(5,10), pady=8, sticky="w")
        else:
            # if no winner then displaying other details
            total_count = self.controller.db.get_player_count_in_tournament(t_id)
            eliminated_count = self.controller.db.get_players_count_eliminated(t_id)
            competing_count = total_count - eliminated_count
            current_round = self.controller.db.get_current_round(t_id)
            ttk.Label(win, text="Round:").grid(row=5, column=0, padx=(20,10), pady=8, sticky="e")
            ttk.Label(win, text=current_round if current_round > 0 else "Final").grid(row=5, column=1, padx=(5,10), pady=8, sticky="w")
            ttk.Label(win, text="Players competing:").grid(row=6, column=0, padx=(20,10), pady=8, sticky="e")
            ttk.Label(win, text=competing_count).grid(row=6, column=1, padx=(5,10), pady=8, sticky="w")
            ttk.Label(win, text="Players eliminated:").grid(row=7, column=0, padx=(20,10), pady=8, sticky="e")
            ttk.Label(win, text=eliminated_count).grid(row=7, column=1, padx=(5,10), pady=8, sticky="w")

        # action buttons
        back_btn = ttk.Button(win, text="Back", command=win.destroy, style="UnHover.TButton")
        back_btn.grid(row=8, column=0, padx=(20,0), pady=8, ipadx=10, sticky="w")
        self.controller.make_hoverable_btn(back_btn, "Hover", "UnHover")

        # if user is logged in then show settings button
        if login_status[0]:
            settings_btn = ttk.Button(win, text="Settings", command=open_settings, style="UnHover.TButton", cursor="spraycan")
            settings_btn.grid(row=8, column=1, padx=(5,20), pady=8, ipadx=5, sticky="w")
            self.controller.make_hoverable_btn(settings_btn, "Hover", "UnHover")
        else:
            # otherwise show a spacer
            spacer = tk.Frame(win, width=90, height=1)
            spacer.grid(row=8, column=1, padx=(5,20), pady=8, sticky="w")

    # building brackets container view
    def open_tournament_brackets(self, t_id: str, login_data: tuple[bool, str | None]):
        # if user is logged in then window title includes the username
        if login_data[0]:
            title = f"Tournament Brackets - Logged in as {login_data[1]}"
        else:
            # otherwise displays guest user
            title = "Tournament Brackets - Guest User"
        self.bracket_win = tk.Toplevel(self)
        self.bracket_win.title(title)
        self.bracket_win.grab_set()
        self.bracket_win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        self.bracket_win.resizable(False, False)

        # making container
        self.brackets_container = ttk.Frame(self.bracket_win)
        self.brackets_container.pack(fill="both", expand=True)

        # building brackets with specified tournament id
        self._build_brackets(t_id, login_data)

    # building actual brackets content view
    def _build_brackets(self, t_id: str, login_data: tuple[bool, str | None]):
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
        def make_frame(gp_id: str, round_frame: ttk.Frame):
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
                colour = "Black.TLabel"
                if self.controller.db.get_race_count_in_gp(gp_id) == 4:
                    wins = self.controller.db.find_winners_for_gp(gp_id)
                    if type(wins) == tuple:
                        if name == wins:
                            colour = "Green.TLabel"
                    else:
                        fmap = [p[0] for p in wins]
                        if name[0] in fmap: 
                            colour = "Green.TLabel"
                
                result = self.controller.db.get_tournament_result(t_id, name[0])
                text = f"{name[1]}: {result}" if result else name[1]
                ttk.Label(match_frame, text=text, anchor="w", style=colour).pack(fill="x")
            
            # filling with blank lines if not all players qualified yet
            for _ in range((4-len(gp_players))):
                ttk.Label(match_frame, text="", anchor="w").pack(fill="x")

            # fetching current race and player count in the gp
            current_r_count = self.controller.db.get_race_count_in_gp(gp_id)
            current_p_count = self.controller.db.get_player_count_in_gp(gp_id)

            # if user is logged in then show input buttons
            if login_data[0]:
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
        
        # function to go to winner statistics view and close this current view
        def goToWinner(w: tuple[str, str, str, int]):
            self.controller.open_statistics_player(w)
            self.bracket_win.destroy()

        # finding the winner
        winner = self.controller.db.read_tournament_winner(t_id)
        if winner is not None:
            # if there is a winner then show the name
            # binding the name to open statistics view with the player data
            # making the label clickable and showing the underline on hover
            winner_label = ttk.Label(self.brackets_container, text=f"Winner: {winner[1]}", font=("TkDefaultFont", 12, "bold"))
            winner_label.grid(row=1, column=len(rounds_joined)//2, pady=20)
            winner_label.bind("<Button-1>", lambda e, w=winner: goToWinner(w))
            self.controller.make_hoverable(winner_label, size=12, weight="bold")

        def go_back():
            self.open_tournament_overview(t_id)
            self.bracket_win.destroy()

        ttk.Button(self.brackets_container, text="Back", command=go_back).grid(row=2, column=0, pady=10, sticky="w")

    # refreshing the brackets after grand prix result input
    def refresh_brackets(self, t_id: str):
        self._build_brackets(t_id)
    
    # opens subview to input race results
    def open_input_race_results(self, gp_id: str, t_id: str):
        # getting the number of races data is entered for to display in title
        race_count = self.controller.db.get_race_count_in_gp(gp_id)
        win = tk.Toplevel(self)
        win.title(f"Input Race Results [{race_count + 1}/4]")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)

        # getting all the circuit names
        # mapping all the circuit names to the circuit
        circuits = self.controller.db.read_circuit_data()
        circuit_names = [c[1] for c in circuits]
        name_to_circuit = {c[1]: c for c in circuits}

        # frame for the circuit selection
        select_circuit_frame = ttk.LabelFrame(win, text="Select the circuit")
        select_circuit_frame.pack(padx=10, pady=10)

        # drop down selection box with all circuits
        circuit_var = tk.StringVar()
        circuit_dropdown = ttk.Combobox(select_circuit_frame, textvariable=circuit_var, values=circuit_names, state="readonly")
        circuit_dropdown.pack(padx=20, pady=10)
        circuit_dropdown.bind("<Escape>", lambda e: win.focus())
        circuit_dropdown.bind("<<ComboboxSelected>>", lambda e: win.focus())
        
        # getting list of players in the grand prix
        players = self.controller.db.read_grand_prix_players(gp_id)
        result_vars = {}

        # frame for the player results selection
        inp_results_frame = ttk.LabelFrame(win, text="Input player results")
        inp_results_frame.pack(padx=10, pady=10)
        
        # for each player in the race, creating a result selction box 1-12
        for p in players:
            # creating a row frame to position the name and dropdown
            row_frame = ttk.Frame(inp_results_frame)
            row_frame.pack(padx=30, fill="x")

            # name label and the dropdown box
            # width 5 as only numbers in the dropdown
            ttk.Label(row_frame, text=p[1]).pack(padx=20, side="left")
            result_var = tk.StringVar()
            result_dropdown = ttk.Combobox(row_frame, textvariable=result_var, values=[str(i) for i in range(1, 13)], state="readonly", width="5")
            result_dropdown.pack(padx=20, side="right")
            result_dropdown.bind("<Escape>", lambda e: win.focus())
            result_dropdown.bind("<<ComboboxSelected>>", lambda e: win.focus())
            result_vars[p[0]] = result_var

        # function to submit the results with validation
        def insert_results():
            # fetching the chosen circuit
            chosen_name = circuit_var.get()
            # if selection is nothing then shows error to select a circuit
            if chosen_name == "":
                messagebox.showerror("Missing Info", "Please select a circuit.")
                return
            # trying to fetch all the results as integers
            # this fails if not all integers and hence not all results have values
            try:
                # creating an array of integers of all results
                # then converting it into a set to remove duplicates
                raw_results = [int(var.get()) for _, var in result_vars.items()]
                unique_results = set(raw_results)
            except ValueError:
                # if can't convert all results to integer then showing error that not all results have been entered
                messagebox.showerror("Incomplete Data", "Please ensure all players have a position assigned.")
                return
            # if number of unique results is not 4 then means 2 results have the same value so showing error
            if len(unique_results) != 4:
                messagebox.showerror("Duplicate Positions", "Two players cannot finish in the same position.\nPlease check your entries.")
                return
            
            # finding the circuit id from its name
            chosen_circuit = name_to_circuit[chosen_name]
            c_id = chosen_circuit[0]

            # collecting all the players
            # creating the race and adding the players and results to it
            # if this is the last race in gp then open gp results subview
            players_results = [(p_id, int(var.get())) for p_id, var in result_vars.items()]
            self.controller.db.create_race(gp_id, c_id, players_results)
            new_race_count = self.controller.db.get_race_count_in_gp(gp_id)
            if new_race_count == 4: self.open_input_gp_results(gp_id, t_id)
            win.destroy()
            if new_race_count < 4: self.refresh_brackets(t_id)

        # action buttons
        bottom_bar = ttk.Frame(win)
        bottom_bar.pack(fill="x", pady=(6,12))

        cancel_btn = ttk.Button(bottom_bar, text="Cancel", command=win.destroy, style="UnHover.TButton")
        cancel_btn.pack(side="left", padx=10)
        self.controller.make_hoverable_btn(cancel_btn, "Hover", "UnHover")

        submit_btn = ttk.Button(bottom_bar, text="Insert Resuts", command=insert_results, style="UnHoverSubmit.TButton")
        submit_btn.pack(side="right", padx=10)
        self.controller.make_hoverable_btn(submit_btn, "HoverSubmit", "UnHoverSubmit")

    # opens subview to input grand prix results
    def open_input_gp_results(self, gp_id: str, t_id: str):
        win = tk.Toplevel(self)
        win.title("Input Grand Prix Results")
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", self.block_window_closure)
        win.resizable(False, False)

        # getting list of players in the grand prix
        players = self.controller.db.read_grand_prix_players(gp_id)
        result_vars = {}
        
        # frame for the player results selection
        inp_results_frame = ttk.LabelFrame(win, text="Input player results")
        inp_results_frame.pack(padx=10, pady=10)

        for p in players:
            # creating a row frame to position the name and dropdown
            row_frame = ttk.Frame(inp_results_frame)
            row_frame.pack(padx=30, fill="x")

            # name label and the dropdown box
            # width 5 as only numbers in the dropdown
            ttk.Label(row_frame, text=p[1]).pack(padx=20, side="left")
            result_var = tk.StringVar()
            result_dropdown = ttk.Combobox(row_frame, textvariable=result_var, values=[str(i) for i in range(1, 13)], state="readonly", width="5")
            result_dropdown.pack(padx=20, side="right")
            result_dropdown.bind("<Escape>", lambda e: win.focus())
            result_dropdown.bind("<<ComboboxSelected>>", lambda e: win.focus())
            result_vars[p[0]] = result_var

        # function to insert the grand prix results
        def save_gp_results():
            # trying to fetch all the results as integers
            # this fails if not all integers and hence not all results have values
            try:
                # creating an array of integers of all results
                # then converting it into a set to remove duplicates
                raw_results = [int(var.get()) for _, var in result_vars.items()]
                unique_results = set(raw_results)
            except ValueError:
                # if can't convert all results to integer then showing error that not all results have been entered
                messagebox.showerror("Incomplete Data", "Please ensure all players have a position assigned.")
                return
            # if number of unique results is not 4 then means 2 results have the same value so showing error
            if len(unique_results) != 4:
                messagebox.showerror("Duplicate Positions", "Two players cannot finish in the same position.\nPlease check your entries.")
                return
            
            # adding the results of the players to GrandPrixParticipation
            self.controller.db.insert_gp_results(gp_id, result_vars.items())
            
            # finding the top players in the gp
            top_players = self.controller.db.find_winners_for_gp(gp_id)
            new_gp_id = self.controller.db.find_next_gp_id(gp_id)

            # if this is the final bracket
            if new_gp_id == "Tournament finished":
                # setting tournament results for all players
                self.controller.db.set_tournament_results(t_id)
                self.refresh_tournaments()
            else:
                # otherwise add the top players to the next round
                self.controller.db.add_winners_to_gp(top_players, new_gp_id)

            win.destroy()
            self.refresh_brackets(t_id)

        # complete button
        complete_btn = ttk.Button(win, text="Complete Grand Prix", command=save_gp_results, style="UnHoverSubmit.TButton")
        complete_btn.pack(padx=10, pady=(6,12))
        self.controller.make_hoverable_btn(complete_btn, "HoverSubmit", "UnHoverSubmit")