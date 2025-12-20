import tkinter as tk
from tkinter import ttk
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from Utilities.tooltip import create_tooltip
from Utilities.animatedButton import AnimatedButton
from Utilities.FontStyling import Fonts as FS, Colours as FC
# importing relevant tkinter packages
# datetime to convert string dates to datetime objects so can compare the dates in time
# matplotlib libraries to show graphs
# importing tooltip to show tip of what the graph represents in the stats homeview
# importing animatedButton to use custom coloured button
# importing FontStyling to use custom fonts and colours

class StatisticsPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_view()

    # function that builds the main view
    def build_view(self):
        main_frame = ttk.Frame(self)
        main_frame.pack()

        # creating button frame to hold all the statistics button options
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # The different statistics views to show
        # Top players: players with most tournament wins: bar chart
        # Top rivalries: tournament results over time for top 5 playesrs: line graph, calculated by sum of their tournament results divided by number of tournaments played so the 5 players with smallest average tournament result
        # Circuit popularity: most played circuits pie chart
        ## Circuit: who and how many times a player has won at that circuit
        # Player at a circuit: what positions a player has come in that circuit
        ## Player: what positions a player has come in all tournaments, player consistency for race results: box plot
        ## because when clicked on links in other part of the system, it opens these views directly with preselected values

        # defining the button data such as title, function to open, tip text and colour
        buttons_data = [
            ("Top Players", self.show_top_players, "Displays the players with the most\ntournament wins as a bar chart.", FC.blue),
            ("Top Rivalries", self.show_rivalry, "Displays the past tournament results\nfor the top 3 players as a line graph.", FC.green),
            ("Circuit Popularity", self.show_circuit_popularity, "Displays the most raced\ncircuits as a pie chart.", FC.red),
            ("Circuit Analysis", self.open_circuit_analysis, "Displays who has won a circuit\nthe most times as a bar chart.", FC.purple),
            ("Player-Circuit Performance", self.open_player_circuit_performance, "Displays a player's performance\nfor a circuit as a bar chart.", FC.gold),
            ("Player Analysis", self.open_player_analysis, "Displays tournament results for a player\nand a box plot showing their consistency.", FC.dblue)
        ]

        # for loop over all the buttons
        # each button has a tip shown on hover
        for text, command, tooltip, hover_colour in buttons_data:
            # custom width based on the length of text
            btn = AnimatedButton(
                btn_frame, text=text, command=command,
                width=20+len(text)*8, height=40, corner_radius=20,
                base_colour=hover_colour[0], hover_colour=hover_colour[1]
            )
            btn.pack(pady=10)
            create_tooltip(btn, tooltip, True)

    # for the basic graphs, this function opens a new window and displays the graph
    def open_graph_window(self, title: str, figure: Figure):
        # creating a new window with a fixed size
        win = tk.Toplevel(self)
        win.title(title)
        win.resizable(False, False)
        win.geometry("800x600")

        # adding the graph to the window
        canvas = FigureCanvasTkAgg(figure, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # function to show top players by tournament wins
    def show_top_players(self):
        # getting the data from the database
        # data is in format [(name, wins), (name, wins), ...]
        data = self.controller.db.get_top_winners_stats()

        if not data: 
            # Open a window just to tell the user there is no data
            window = tk.Toplevel(self)
            window.title("Top Players")
            window.geometry("400x200")
            window.resizable(False, False)
            
            tk.Label(window, text="No data recorded.\nYou haven't finished a tournament yet!", font=FS.base2).pack(expand=True)
            return

        # arrays for all names and wins, so can plot on x and y axis
        names = [row[0] for row in data]
        wins = [row[1] for row in data]

        # creating the figure
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)
        # adding the data to chart, and setting titles and labels
        ax.bar(names, wins, color=FC.blue[0])
        ax.set_title("Top Players by Tournament Wins")
        ax.set_ylabel("Wins")
        ax.set_xlabel("Player")
        ax.yaxis.get_major_locator().set_params(integer=True)
        
        # rotate labels if names are long
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        # calling function to show the graph in a new window
        self.open_graph_window("Top Players", fig)

    # function to show the top 5 players past tournament results
    def show_rivalry(self):
        # getting the data from the database
        # data is in format {name: [(date, result), (date, result), ...], name: [...], ...}
        data_dict = self.controller.db.get_rivalry_stats()

        if not data_dict:
            # Open a window just to tell the user there is no data
            window = tk.Toplevel(self)
            window.title("Rivalry Analysis")
            window.geometry("400x200")
            window.resizable(False, False)
            
            tk.Label(window, text="No data recorded.\nYou haven't finished a tournament yet!", font=FS.base2).pack(expand=True)
            return

        # creating the figure
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)

        # adding results for each player to the graph
        for name, records in data_dict.items():
            # sort by date (converting string date to datetime object for sorting)
            records.sort(key=lambda x: datetime.strptime(x[0], "%d/%m/%y"))
            # arrays of all dates and results
            # array for dates is as datetime objects not strings
            date_objects = [datetime.strptime(r[0], "%d/%m/%y") for r in records]
            results = [r[1] for r in records]
            # adding the data to the chart
            ax.plot(date_objects, results, marker="o", label=name)

        # setting titles and labels
        ax.set_title("Tournament Results Over Time (Top 5 Players)") # graph title
        ax.set_ylabel("Position") # y axis title
        ax.set_xlabel("Date") # x axis title
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y')) # turning datetime objects back to strings
        fig.autofmt_xdate() # auto rotate dates if they overlap
        ax.invert_yaxis() # 1st place at top
        ax.set_yticks(range(1, 17)) # showing y axis ticks 1-16
        ax.set_ylim(16.5, 0.5) # so that there is spacing on bottom and top
        ax.legend() # showing legend
        ax.tick_params(axis="x", rotation=45) # rotating x axis data titles
        fig.tight_layout()

        # calling function to show the graph in a new window
        self.open_graph_window("Rivalry Analysis", fig)

    # function to show popularity of circuits
    def show_circuit_popularity(self):
        # getting the data from the database
        # data is in format [(circuit_name, count), (circuit_name, count), ...]
        data = self.controller.db.get_circuit_usage_stats()
        
        if not data:
            # Open a window just to tell the user there is no data
            window = tk.Toplevel(self)
            window.title("Circuit Popularity")
            window.geometry("400x200")
            window.resizable(False, False)
            
            tk.Label(window, text="No races recorded.\nYou haven't raced on any circuits yet!", font=FS.base2).pack(expand=True)
            return
        
        # inner function to calculate the proportions for pie chart
        def calculate_sizes(data: list[tuple[str, str]]) -> tuple[list[str], list[int]]:
            # setting a max number of slices for the pie chart as 10
            # if there are more than 10 items from data then must group some into other category
            # but can't simply cut off at the end, must make sure count of last item is greater than max count of other items
            MAX_TOTAL_SLICES = 10
            MAX_SPECIFIC_SLICES = 9 # Indices 0 to 8

            # empty arrays of labels and sizes
            labels = []
            sizes = []

            # case 1: there is 10 or fewer items, so we can show all directly
            if len(data) <= MAX_TOTAL_SLICES:
                # array for labels and sizes for pie chart
                labels = [row[0] for row in data]
                sizes = [int(row[1]) for row in data]
                return labels, sizes

            # case 2: there are more than 10 items, so we need to group some into other category
            else:
                # we want to verify that the last item we keep is strictly greater than the first item we drop into other
                # start assuming we keep the top 9
                split_index = MAX_SPECIFIC_SLICES
                
                # the value of the first item that would normally go into "Other"
                cutoff_value = data[split_index][1] # count of the 10th item

                # decrementing the split index while the count of the last kept item equals the cutoff
                # we continue until we find an item that is larger than the cutoff
                while split_index > 0 and data[split_index - 1][1] == cutoff_value:
                    split_index -= 1

                # if split_index becomes 0, it means all items are equal (or top 10 are equal)
                # in that case it better to just show the top 9, instead of showing 1 great other slice
                # but assuming normal data, split_index will be somewhere between 1 and 9
                if split_index == 0:
                    # reverting back to use top 9, and then rest into other
                    split_index = MAX_SPECIFIC_SLICES

                # slice the data based on our calculated fair point
                top_data = data[:split_index]
                remaining_data = data[split_index:]
                
                # calculate sum of count for other category
                other_count = sum(int(row[1]) for row in remaining_data)
                
                # creating the labels and sizes arrays
                labels = [row[0] for row in top_data] + [f"Other ({len(remaining_data)})"]
                sizes = [int(row[1]) for row in top_data] + [other_count]
                return labels, sizes
        
        # arrays for labels and sizes for pie chart
        labels, sizes = calculate_sizes(data)

        # creating the figure
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)

        # creating the pie chart with labels and sizes, showing as percentages and starting from top
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        ax.set_title("Most Frequently Raced Circuits")

        # calling function to show the graph in a new window
        self.open_graph_window("Circuit Popularity", fig)

    # function to show who has most wins at a circuit
    def open_circuit_analysis(self, circuit: tuple[str, str] | None = None):
        # getting the number of players, if no player created then showing message
        player_count = self.controller.db.get_player_count()
        if player_count == 0:
            # Open a window just to tell the user there are no players to view statistics on
            window = tk.Toplevel(self)
            window.title("Circuit Analysis")
            window.geometry("400x200")
            window.resizable(False, False)
            
            tk.Label(window, text="You haven't created any players.\nNo one has raced yet!", font=FS.base2).pack(expand=True)
            return
        
        # creating a new window
        win = tk.Toplevel(self)
        win.title("Circuit Analysis")
        win.resizable(False, False)
        win.geometry("800x750")

        # creating header frame for circuit selection and images
        header_frame = ttk.Frame(win)
        header_frame.pack(side=tk.TOP, fill="x", pady=10, padx=20)
        header_frame.columnconfigure(1, weight=1)

        # creating placeholder for circuit cover image, column 0 for left side
        win.img_left_label = ttk.Label(header_frame)
        win.img_left_label.grid(row=0, column=0, sticky="w")

        # creating frame for circuit selection, column 1 for middle
        control_frame = ttk.Frame(header_frame)
        control_frame.grid(row=0, column=1)
        ttk.Label(control_frame, text="Circuit:").pack(side=tk.LEFT)
        
        # getting all circuits from database
        # arrays of all circuit names and ids
        circuits = self.controller.db.read_circuit_data()
        circuit_names = [c[1] for c in circuits]
        circuit_ids = [c[0] for c in circuits]

        # creating the dropdown box with all the circuit names
        combo = ttk.Combobox(control_frame, values=circuit_names, state="readonly")
        combo.pack(side=tk.LEFT, padx=5)
        combo.bind("<Escape>", lambda e: win.focus())
        combo.bind("<<ComboboxSelected>>", lambda e: win.focus())
        # if a circuit is provided, preselect it (when hyperlink clicked in circuit view)
        if circuit: combo.set(f"{circuit[1]}")

        # creating placeholder for circuit map image, column 2 for right side
        win.img_right_label = ttk.Label(header_frame)
        win.img_right_label.grid(row=0, column=2, sticky="e")

        # creating a placeholder for the canvas
        win.canvas = None

        # initial error message informing user to select a circuit
        win.error_label = tk.Label(win, text="Please select a circuit to analyse.", font=FS.base2_i, fg=FC.cancel)
        win.error_label.pack(expand=True)

        # when dropdown selected then draw the graph
        combo.bind("<<ComboboxSelected>>", lambda e: self.draw_circuit_winners(win, combo, circuit_ids))
        # if circuit provided then draw it immediately (when hyperlink clicked in circuit view)
        if circuit: self.draw_circuit_winners(win, combo, circuit_ids)

    # function to draw the circuit winners graph
    def draw_circuit_winners(self, win: tk.Toplevel, combo: ttk.Combobox, circuit_ids: list[str]):
        # getting the index of the selected circuit
        # if -1 then nothing selected so return
        idx = combo.current()
        if idx == -1: return
        # getting the circuit id and name based on the selected index
        c_id = circuit_ids[idx]
        c_name = combo.get()

        # replacing spaces with _ in circuit name for filename
        filename = "_".join(c_name.split(" "))
        # defining the path to the file
        BASE_PATH = f"Mario Kart Images/Resized/{filename}_[] Small.png"

        # function to load an image into the widget
        def load_image_to_label(path, label_widget):
            # trying to load photo from path
            try:
                photo = tk.PhotoImage(file=path)
                label_widget.config(image=photo, text="")
                label_widget.image = photo
                # setting the label image to the photo file
            except Exception:
                # Fallback if image not found
                label_widget.config(image="", text="No Image")

        # loading the images to their placeholder labels defined in open_circuit_analysis above
        load_image_to_label(BASE_PATH.replace("[]", "COVER"), win.img_left_label)
        load_image_to_label(BASE_PATH.replace("[]", "MAP"), win.img_right_label)

        # getting the data from the database
        # data is in format [(player_name, wins), (player_name, wins), ...]
        data = self.controller.db.get_circuit_winners(c_id)
        
        # if already a graph shown then destroy it
        if win.canvas: 
            win.canvas.get_tk_widget().destroy()
            win.canvas = None

        # if there is an error message shown then destroy it
        if hasattr(win, "error_label") and win.error_label:
            win.error_label.destroy()
            win.error_label = None

        # if no data then show error message, indicates that no one has won at that circuit yet
        if not data:
            win.error_label = tk.Label(win, text=f"No one has come 1st place in {c_name} yet.", font=FS.base2)
            win.error_label.pack(pady=50, expand=True)
            return

        # arrays for all names and wins, so can plot on x and y axis
        names = [row[0] for row in data]
        wins = [row[1] for row in data]

        # creating the figure
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)
        # creating the bar chart with the data, and setting titles and labels
        bars = ax.bar(names, wins, color=FC.gold[0], edgecolor=FC.gold[1])
        ax.set_title(f"Most Wins at {c_name}")
        ax.set_ylabel("Wins")
        ax.yaxis.get_major_locator().set_params(integer=True)
        ax.tick_params(axis="x", rotation=20)
        ax.bar_label(bars)
        fig.tight_layout()
        # adding the graph to the window
        win.canvas = FigureCanvasTkAgg(fig, master=win)
        win.canvas.draw()
        win.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # function to show a players 1st 2nd and 3rd place counts at a circuit
    def open_player_circuit_performance(self):
        # getting the number of players, if no player created then showing message
        player_count = self.controller.db.get_player_count()
        if player_count == 0:
            # Open a window just to tell the user there are no players to view statistics on
            window = tk.Toplevel(self)
            window.title("Player-Circuit Performance")
            window.geometry("400x200")
            window.resizable(False, False)
            
            tk.Label(window, text="You haven't created any players.\nThere isn't any data to view statistics on yet!", font=FS.base2).pack(expand=True)
            return
        
        # creating a new window
        win = tk.Toplevel(self)
        win.title("Player-Circuit Performance")
        win.resizable(False, False)
        win.geometry("800x600")

        # creating frame for circuit selection
        # fetching data and making arrays for circuit names and ids
        control_frame = ttk.Frame(win)
        control_frame.pack(side=tk.TOP, pady=(15,0))
        ttk.Label(control_frame, text="Circuit:").pack(side=tk.LEFT, padx=(0, 5))
        circuits = self.controller.db.read_circuit_data()
        c_names = [c[1] for c in circuits]
        c_ids = [c[0] for c in circuits]
        # circuit dropdown with all circuit names
        c_combo = ttk.Combobox(control_frame, values=c_names, state="readonly", width=20)
        c_combo.pack(side=tk.LEFT, padx=(0, 15))
        c_combo.bind("<Escape>", lambda e: win.focus())
        c_combo.bind("<<ComboboxSelected>>", lambda e: win.focus())

        # creating frame for player selection
        # fetching data and making arrays for player names and ids
        ttk.Label(control_frame, text="Player:").pack(side=tk.LEFT, padx=(0, 5))
        players = self.controller.db.read_player_data()
        p_names = [f"{p[1]} {p[2]}" for p in players]
        p_ids = [p[0] for p in players]
        # player dropdown with all player names
        p_combo = ttk.Combobox(control_frame, values=p_names, state="readonly", width=20)
        p_combo.pack(side=tk.LEFT)
        p_combo.bind("<Escape>", lambda e: win.focus())
        p_combo.bind("<<ComboboxSelected>>", lambda e: win.focus())

        # creating a placeholder for the canvas
        win.canvas = None

        # initial error message informing user to select a circuit
        win.error_label = tk.Label(win, text="Please select both a Circuit and a Player to view performance stats.", font=FS.base2_i, fg=FC.cancel)
        win.error_label.pack(expand=True)

        # when dropdowns selected then draw the graph
        c_combo.bind("<<ComboboxSelected>>", lambda e: self.draw_player_circuit_stats(win, c_combo, p_combo, c_ids, p_ids))
        p_combo.bind("<<ComboboxSelected>>", lambda e: self.draw_player_circuit_stats(win, c_combo, p_combo, c_ids, p_ids))

    # function to draw the player circuit performance graph
    def draw_player_circuit_stats(self, win: tk.Toplevel, c_combo: ttk.Combobox, p_combo: ttk.Combobox, c_ids: list[str], p_ids: list[str]):
        # checking if both dropdowns have a selection
        c_idx = c_combo.current()
        p_idx = p_combo.current()

        # -1 indicates no selection to return
        if c_idx == -1 or p_idx == -1:
            return

        # getting the circuit and player ids and names
        c_id = c_ids[c_idx]
        p_id = p_ids[p_idx]
        p_name = p_combo.get()
        c_name = c_combo.get()

        # if already a graph shown then destroy it
        if win.canvas: 
            win.canvas.get_tk_widget().destroy()
            win.canvas = None

        # if there is an error message shown then destroy it
        if hasattr(win, "error_label") and win.error_label:
            win.error_label.destroy()
            win.error_label = None

        # fetching the data from the database
        # data is in format [(position, count), (position, count), ...]
        data = self.controller.db.get_player_circuit_results(c_id, p_id)

        # defining positions and counts arrays for x and y axis
        positions = ["1st", "2nd", "3rd"]
        counts = [0, 0, 0]

        # if data exists then populate counts array
        if data:
            for row in data:
                # for each position and count
                pos = row[0] 
                count = row[1]
                # ensure pos is an integer and within range
                if isinstance(pos, int) and 1 <= pos <= 3:
                    counts[pos-1] = count
        
        # if no data then show error message, indicates that the player hasn't raced at that circuit yet
        if not data:
            win.error_label = tk.Label(win, text=f"No race results found for {p_name} at {c_name}.", font=FS.base2)
            win.error_label.pack(pady=50, expand=True)
            return

        # if sum of counts is 0, indicates that the player has raced but never finished in top 3
        if sum(counts) == 0:
            win.error_label = tk.Label(win, text=f"{p_name} has raced at {c_name},\nbut never finished in the Top 3.", font=FS.base2)
            win.error_label.pack(pady=50, expand=True)
            return
        
        # creating the figure
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # creating bar chart with titles and labels
        bars = ax.bar(positions, counts, color=FC.gold_silver_bronze)        
        ax.set_title(f"{p_name}'s Top Results at {c_combo.get()}")
        ax.set_ylabel("Times Achieved")
        ax.yaxis.get_major_locator().set_params(integer=True)
        ax.bar_label(bars)
        fig.tight_layout()
        # adding the graph to the window
        win.canvas = FigureCanvasTkAgg(fig, master=win)
        win.canvas.draw()
        win.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # function to show a player's past tournament results and their consistency
    def open_player_analysis(self, player: tuple[str, str, str, int] | None = None):
        # getting the number of players, if no player created then showing message
        player_count = self.controller.db.get_player_count()
        if player_count == 0:
            # Open a window just to tell the user there are no players to analyse
            window = tk.Toplevel(self)
            window.title("Full Player Analysis")
            window.geometry("400x200")
            window.resizable(False, False)
            
            tk.Label(window, text="You haven't created any players.\nThere is no data to view analyse yet!", font=FS.base2).pack(expand=True)
            return
        
        # creating a new window
        win = tk.Toplevel(self)
        win.title("Full Player Analysis")
        win.resizable(False, False)
        win.geometry("880x800")

        # creating frame for player selection
        control_frame = ttk.Frame(win)
        control_frame.pack(side=tk.TOP, pady=(15,0))
        ttk.Label(control_frame, text="Player:").pack(side=tk.LEFT)
        
        # getting all players from database
        # arrays of all player names and ids
        players = self.controller.db.read_player_data()
        p_names = [f"{p[1]} {p[2]}" for p in players]
        p_ids = [p[0] for p in players]

        # creating the dropdown box with all the player names
        combo = ttk.Combobox(control_frame, values=p_names, state="readonly", width=30)
        combo.pack(side=tk.LEFT, padx=5)
        combo.bind("<Escape>", lambda e: win.focus())
        combo.bind("<<ComboboxSelected>>", lambda e: win.focus())
        # if a player is provided, preselect it (when hyperlink clicked in player view)
        if player: combo.set(f"{player[1]} {player[2]}")

        # creating frames for the two graphs
        win.top_graph_frame = ttk.Frame(win)
        win.top_graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        win.bottom_graph_frame = ttk.Frame(win)
        win.bottom_graph_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # creating a placeholder for the canvases
        win.canvas_line = None
        win.canvas_box = None

        # initial error message informing user to select a player
        win.error_label = tk.Label(win, text="Please select a player to analyse.", font=FS.base2_i, fg=FC.cancel)
        win.error_label.pack(expand=True)

        # when dropdown selected then draw the graphs
        combo.bind("<<ComboboxSelected>>", lambda e: self.draw_player_analysis(win, combo, p_ids))
        # if player provided then draw it immediately (when hyperlink clicked in player view)
        if player: self.draw_player_analysis(win, combo, p_ids)

    # function to draw the player analysis graphs
    def draw_player_analysis(self, win: tk.Toplevel, combo: ttk.Combobox, p_ids: list[str]):
        # getting the index of the selected player
        # if -1 then nothing selected so return
        idx = combo.current()
        if idx == -1: return
        # getting the player id and name based on the selected index
        p_id = p_ids[idx]
        p_name = combo.get()

        # fetching the data from the database
        # history_data is in format [(date, result), (date, result), ...]
        history_data = self.controller.db.get_player_history(p_id)
        
        # if already a graph shown then destroy it
        if win.canvas_line: 
            win.canvas_line.get_tk_widget().destroy()
            win.canvas_line = None
        if win.canvas_box: 
            win.canvas_box.get_tk_widget().destroy()
            win.canvas_box = None

        # if there is an error message shown then destroy it
        if hasattr(win, "error_label") and win.error_label:
            win.error_label.destroy()
            win.error_label = None
        
        # if no data then show error message, indicates that the player hasn't participated in any tournaments yet
        if not history_data:
            # Hide the graph frames
            win.top_graph_frame.pack_forget()
            win.bottom_graph_frame.pack_forget()
            win.error_label = tk.Label(win, text=f"No data found for {p_name}.", font=FS.base2)
            win.error_label.pack(expand=True)
            return
        
        # Showing the graph frames
        win.top_graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        win.bottom_graph_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # converting string dates to datetime object
        parsed_data = []
        for date_str, result in history_data:
            try:
                dt = datetime.strptime(date_str, "%d/%m/%y")
                parsed_data.append((dt, result))
            except ValueError: continue
        # sorting by date
        parsed_data.sort(key=lambda x: x[0])
        # arrays for all dates and results, so can plot on x and y axis
        dates = [x[0] for x in parsed_data]
        results = [x[1] for x in parsed_data]

        # creating the line graph figure
        fig1 = Figure(figsize=(8, 4), dpi=100)
        ax1 = fig1.add_subplot(111)
        ax1.plot(dates, results, marker="o", linestyle="-", color=FC.blue[0])
        # adding titles and labels
        ax1.set_title(f"Tournament Placement History: {p_name}")
        ax1.set_ylabel("Position (Lower is Better)")
        ax1.invert_yaxis()
        ax1.set_yticks(range(min(results), max(results)+1)) # showing y axis ticks in range of min and max results values
        ax1.set_ylim(max(results)+0.5, min(results)-0.5) # so that there is spacing on bottom and top by adding/removing 0.5 to min and max results
        fig1.autofmt_xdate()
        ax1.fmt_xdata = mdates.DateFormatter("%d/%m/%y")
        fig1.tight_layout()
        # adding the line graph to the top frame
        win.canvas_line = FigureCanvasTkAgg(fig1, master=win.top_graph_frame)
        win.canvas_line.draw()
        win.canvas_line.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # fetching race results data for box plot
        # data is in format [result1, result2, result3, ...]
        race_results = self.controller.db.get_race_results(p_id)

        # if there are results
        if race_results:
            # creating the box plot figure
            fig2 = Figure(figsize=(8, 2), dpi=100)
            ax2 = fig2.add_subplot(111)
            # creating the box plot with the results
            ax2.boxplot(race_results, vert=False, labels=["Race Results"])
            ax2.tick_params(axis="y", labelrotation=90)
            # adding titles and labels
            ax2.set_title(f"Consistency Analysis: {p_name}")
            ax2.set_xlabel("Race Finish Position")
            # if only 1 result or results are all the same
            if len(set(race_results)) == 1:
                ax2.set_xticks(range(race_results[0]-1, race_results[0]+2)) # show ticks for ±1 of the result
                ax2.set_xlim(race_results[0]-1.5, race_results[0]+1.5) # graph scale is ±1.5 of the result
            else:
                # if more than 1 unique result then a proper bar chart is shown, setting the x axis ticks to integers only
                ax2.xaxis.get_major_locator().set_params(integer=True)
            ax2.invert_yaxis()
            fig2.tight_layout()
            # adding the box plot to the bottom frame
            win.canvas_box = FigureCanvasTkAgg(fig2, master=win.bottom_graph_frame)
            win.canvas_box.draw()
            win.canvas_box.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            # otherwise shows empty canvas, but error message will show
            win.canvas_box = None

    # When hyperlinks clicked in other parts of the system, these functions open the relevant graphs directly with preselected values
    def load_player_stats(self, player:  tuple[str, str, str, int]):
        self.open_player_analysis(player)

    def load_circuit_stats(self, circuit: tuple[str, str]):
        self.open_circuit_analysis(circuit)