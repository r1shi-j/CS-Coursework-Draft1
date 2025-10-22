import tkinter as tk
from tkinter import ttk

class CircuitsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Circuits Page", font=("Arial", 14)).pack(pady=20)

        self.build_view()

    def build_view(self):
        self.form_frame = ttk.Frame(self)
        self.form_frame.pack(pady=10, fill="x")

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # creating the scroll container
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(self.form_frame, text="Search circuits:").grid(row=0, column=0, padx=5, pady=2, sticky="e")

        # creating the search field textbox
        self.search_field = ttk.Entry(self.form_frame, width=20)
        self.search_field.grid(row=0, column=1, padx=5, pady=2)

        # when any key is pressed it will search which is for real time searching
        # binding cmd del to clear search field
        self.search_field.bind("<KeyRelease>", self.search_circuits)
        self.search_field.bind("<Command-BackSpace>", self.clear_entry)

        # clear search button
        rmv_search_btn = ttk.Button(self.form_frame, text="⌫", width=2, command=self.remove_search)
        rmv_search_btn.grid(row=0, column=2, padx=2)

        # the container for the search results
        self.results_frame = ttk.Frame(canvas)
        self.results_frame.pack(fill="both", expand=True)
        canvas_window = canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.results_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        # initially showing all circuits (no search query)
        self.show_results(self.controller.db.read_circuit_data())

    # function to display the search results
    def show_results(self, results):
        # first clear current results
        self.clear_results()
        
        # if no items found for query then display this message
        if not results:
            ttk.Label(self.results_frame, text="No circuits found.").pack(pady=10)
            return

        # creating a row with the text for each result
        for row in results:
            row_frame = ttk.Frame(self.results_frame)
            row_frame.pack(fill="x", pady=2)

            # TODO: each circuit should be a button when clicked goes to stats view for that circuit
            ttk.Label(row_frame, text=row[1], width=20, anchor="w").pack(side="left")

    # function to clear the search field by deleting content in the text box
    def clear_entry(self, event=None):
        self.search_field.delete(0, tk.END)

    # function to clear the search results by removing all content in that frame
    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    # function to search circuits
    def search_circuits(self, event=None):
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
    def remove_search(self):
        self.clear_entry()
        self.show_results(self.controller.db.read_circuit_data())
        