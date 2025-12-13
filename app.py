import tkinter as tk
from tkinter import ttk, messagebox
from storage import Database
from Pages import tournaments, players, circuits, statistics
# importing relevant tkinter packages
# importing Database class from storage file
# importing the view files from Pages folder

# creating the frame
class App(tk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        # creating the view
        self.master = master
        # when user tries to close window the function on_app_close is called
        self.master.protocol("WM_DELETE_WINDOW", self.on_app_close)
        # creating and connecting to the database
        self.db = Database()
        self.db.connect()
        # calling functions to create style and basic view
        self.create_styling()
        self.create_layout()
        # dictionary for the header frames
        self.frames = {}
        # creating the navbar and view pages, and then showing the Tournaments frame
        self.create_navbar()
        self.create_pages()
        self.show_frame("Tournaments")
    
    # function called when window is tried to be closed
    def on_app_close(self):
        # showing confirmation dialogue to check they want to close the system
        confirmed = messagebox.askokcancel("Help", "Are you sure you want to close the system?", default="cancel")
        if confirmed:
            # if they say ok then first close the database and then close the window
            self.db.close()
            self.master.quit()

    # function to creating styling to use for different buttons
    def create_styling(self):
        style = ttk.Style()
        style.configure("HoverDelete.TButton", foreground="#df3832", font=("TkDefaultFont", 10, "underline"))
        style.configure("UnHoverDelete.TButton", foreground="#df3832", font=("TkDefaultFont", 10, "normal"))
        style.configure("HoverSubmit.TButton", foreground="#00a2ff", font=("TkDefaultFont", 10, "underline"))
        style.configure("UnHoverSubmit.TButton", foreground="#00a2ff", font=("TkDefaultFont", 10, "normal"))
        style.configure("Hover.TButton", font=("TkDefaultFont", 10, "underline"))
        style.configure("UnHover.TButton", font=("TkDefaultFont", 10, "normal"))
        style.configure("Black.TLabel", foreground="#000000")
        style.configure("Green.TLabel", foreground="#11DF11")
        # creating hover and non hover variants with underline and no underline respectively

    # creating the layout
    def create_layout(self):
        # setting name, minimum size and disabling user resizing of the window
        self.master.title("Mario Kart Tournament System")
        self.master.minsize(600, 400)
        self.master.resizable(False, False)
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill="both", expand=True)

        # creating the header frame for navigation buttons
        self.header_frame = ttk.Frame(main_frame)
        self.header_frame.pack(fill="x", pady=(15, 5))

        # creating the separator
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", padx=10, pady=5)

        # creating the container for view content
        self.container = ttk.Frame(main_frame)
        self.container.pack(fill="both", expand=True)

    # creates the navigation bar
    def create_navbar(self):
        self.nav_labels = {}

        # function to make navigation label
        def make_nav_label(parent: ttk.Frame, view_name: str):
            # creating the title
            label = ttk.Label(parent, text=view_name, font=("TkDefaultFont", 12))
            label.pack(side="left", padx=40)

            # adding underline when hover
            def on_enter(e):
                # if hovered title is not the current page then underline it
                if self.current_page != view_name:
                    label.configure(font=("TkDefaultFont", 12, "underline"))

            # remove underline when not hovering
            def on_leave(e):
                # if hovered title is not the current page then remove underline
                if self.current_page != view_name:
                    label.configure(font=("TkDefaultFont", 12))

            # when label clicked call function to show that view
            def on_click(e): self.show_frame(view_name)

            # binding mouse actions to these functions
            label.bind("<Enter>", on_enter)
            label.bind("<Leave>", on_leave)
            label.bind("<Button-1>", on_click)
            # in dictionary setting the view title to the actual label variable
            self.nav_labels[view_name] = label
            return label

        # making all the headers
        make_nav_label(self.header_frame, "Tournaments")
        make_nav_label(self.header_frame, "Players")
        make_nav_label(self.header_frame, "Circuits")
        make_nav_label(self.header_frame, "Statistics")

        # defining the current page to be None
        # when app runs this is set to Tournaments
        self.current_page = None

    # linking the view classes to run when clicked on their header
    def create_pages(self):
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        # for loop for each of the classes (from their respective files)
        for file in (tournaments.TournamentsPage, players.PlayersPage, circuits.CircuitsPage, statistics.StatisticsPage):
            # getting the view name from the class by removing Page from TournamentsPage etc
            page_name = file.__name__.replace("Page", "")
            # making the class which calls the initialiser function which builds the frame, passing in the container frame and self to use to access the database
            frame = file(self.container, self)
            # adding the frame to the dictionary of view names
            self.frames[page_name] = frame
            # placing the view in the container sticking to all sides 
            frame.grid(row=0, column=0, sticky="nsew")

    # showing the respective frame when navigation button clicked on
    def show_frame(self, page_name: str):
        # getting the frame from dictionary with the page name
        # tkraise to bring that view to the top
        frame = self.frames[page_name]
        frame.tkraise()

        # adding or removing the blue font colour to current view title
        for name, label in self.nav_labels.items():
            # getting the name and label for all nav titles
            if name == page_name:
                # making the foreground blue for the selected view
                label.configure(font=("TkDefaultFont", 12, "underline"), foreground="blue")
            else:
                # making the foreground black for the selected view
                label.configure(font=("TkDefaultFont", 12), foreground="black")

        # setting the current page to selected page
        self.current_page = page_name

    # function to underline a label on hover
    # takes optional parameters for font size and weight
    def make_hoverable(self, label: ttk.Label, size: int | None = None, weight: str | None = None):
        # defining the base and hover font where hover has an underline
        base_font = ("TkDefaultFont", size if size else 10, weight if weight else "normal")
        hover_font = ("TkDefaultFont", size if size else 10, f"{weight} underline" if weight else "underline")
        # binding enter and leave hover actions over the label to change the font
        label.bind("<Enter>", lambda e: label.config(font=hover_font))
        label.bind("<Leave>", lambda e: label.config(font=base_font))

    # function to underline a button on hover
    def make_hoverable_btn(self, button: ttk.Button, h: str, uh: str):
        # binding enter and leave hover actions over the button to change the button style
        # parameters for differnt styles, could have delete, submit or standard styles
        button.bind("<Enter>", lambda e: button.config(style=f"{h}.TButton"))
        button.bind("<Leave>", lambda e: button.config(style=f"{uh}.TButton"))

    # function to open statistics view with player data
    def open_statistics_player(self, player: tuple[str, str, str, int]):
        # calling function to load player stats
        stats_page = self.frames["Statistics"]
        stats_page.load_player_stats(player)
        # loading the statistics view
        self.show_frame("Statistics")

    # function to open statistics view with circuit data
    def open_statistics_circuit(self, circuit: tuple[str, str]):
        # calling function to load circuit stats
        stats_page = self.frames["Statistics"]
        stats_page.load_circuit_stats(circuit)
        # loading the statistics view
        self.show_frame("Statistics")