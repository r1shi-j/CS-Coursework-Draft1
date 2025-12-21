import tkinter as tk
from tkinter import ttk
from Utilities.tooltip import create_tooltip
from Utilities.FontStyling import Colours as FC
# importing relevant tkinter packages
# importing tooltip to show the circuit cover on hovern
# importing FontStyling to use custom colours

class CircuitsPage(ttk.Frame):
    def __init__(self, parent: ttk.Frame, controller):
        super().__init__(parent)
        self.controller = controller
        self.build_view()

    # building the circuits view homepage with search bar and list of circuits
    def build_view(self):
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack()

        # creating the search bar frame
        search_frame = ttk.Frame(self.form_frame)
        search_frame.pack(pady=(15, 8))

        # subtitle, search field and clear button
        # binding keyboard buttons to clear and unfocus search field, with every keypress triggering a search for real time searching
        # using subtitle style to get font size 12
        ttk.Label(search_frame, text="Search circuits:", style="Subtitle.TLabel").pack(side="left", padx=5)
        self.search_field = ttk.Entry(search_frame, width=20)
        self.search_field.pack(side="left", padx=5)
        self.search_field.bind("<KeyRelease>", self.search_circuits)
        self.search_field.bind(self.CLEAR_TEXT_FIELD, self.clear_entry)
        self.search_field.bind("<Escape>", lambda e: self.search_field.focus_set() or self.focus())
        # clear search button as a label so can add styling
        clear_search = ttk.Label(search_frame, text="⌫", width=2)
        clear_search.pack(side="left", padx=5)

        # binding hover and unhover to change the colour to red on hover
        def on_enter(e): clear_search.config(foreground=FC.red[1])
        def on_leave(e): clear_search.config(foreground=FC.black)
        clear_search.bind("<Enter>", on_enter)
        clear_search.bind("<Leave>", on_leave)
        # binding clicking on the label to call remove search function
        clear_search.bind("<Button-1>", self.remove_search)

        # creating the scroll container
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # the container for the search results
        self.results_frame = ttk.Frame(self.canvas)
        self.results_frame.pack()
        canvas_window = self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        def on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.results_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            self.canvas.itemconfig(canvas_window, width=event.width)
        self.canvas.bind("<Configure>", on_canvas_configure)

        # initially showing all circuits (no search query)
        self.show_results(self.controller.db.read_circuit_data())

    # function to display the search results
    def show_results(self, results: list[tuple[str, str]]):
        # first clear current results
        self.clear_results()
        
        # if no items found for query then display this message
        if not results:
            ttk.Label(self.results_frame, text="No circuits found.").pack(pady=10)
            return

        # creating a row with the text for each result
        # adding extra padding at the bottom of last row
        # binding the name to open statistics view with the circuit data
        # name is underlined on hover
        for row in results:
            name = ttk.Label(self.results_frame, text=row[1], anchor="center")
            # padding of 4 between each row, this is 1 greater than in player view, because each text opens a tip, don't want them to be too close together
            name.pack(pady=(4 if results.index(row) != len(results)-1 else (4,20)))
            name.bind("<Button-1>", lambda e, r=row: self.controller.open_statistics_circuit(r))
            self.controller.make_hoverable(name)
            create_tooltip(name, row[1], False)

    # function to clear the search field by deleting content in the text box
    def clear_entry(self, event=None):
        self.search_field.delete(0, tk.END)

    # function to clear the search results by removing all content in that frame
    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    # function to search circuits
    def search_circuits(self, event=None):
        # scrolling all the way up to top of search results
        self.canvas.yview_moveto(0)

        # fetches the query
        query = self.search_field.get().strip()

        # if query is blank then fetch all circuits
        # else fetch the circuits for the query
        if query == "":
            results = self.controller.db.read_circuit_data()
        else:
            results = self.controller.db.search_circuits(query)
        self.show_results(results)

    # when the clear search button pressed, clear the textbox and then load all circuits
    def remove_search(self, event):
        self.clear_entry()
        self.show_results(self.controller.db.read_circuit_data())