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

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Label(self.form_frame, text="Search circuits:").grid(row=0, column=0, padx=5, pady=2, sticky="e")

        self.search_field = ttk.Entry(self.form_frame, width=20)
        self.search_field.grid(row=0, column=1, padx=5, pady=2)
        
        self.search_field.bind("<KeyRelease>", self.search_circuits)
        self.search_field.bind("<Command-BackSpace>", self.clear_entry)

        rmv_search_btn = ttk.Button(self.form_frame, text="⌫", width=2, command=self.remove_search)
        rmv_search_btn.grid(row=0, column=2, padx=2)

        self.results_frame = ttk.Frame(canvas)
        self.results_frame.pack(fill="both", expand=True)
        canvas_window = canvas.create_window((0, 0), window=self.results_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.results_frame.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)

        self.show_results(self.controller.db.read_circuit_data())

    def show_results(self, results):
        self.clear_results()
        if not results:
            ttk.Label(self.results_frame, text="No circuits found.").pack(pady=10)
            return

        for row in results:
            row_frame = ttk.Frame(self.results_frame)
            row_frame.pack(fill="x", pady=2)

            ttk.Label(row_frame, text=row[1], width=20, anchor="w").pack(side="left")

    def clear_entry(self, event=None):
        self.search_field.delete(0, tk.END)

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def search_circuits(self, event=None):
        query = self.search_field.get().strip()
        if query == "":
            results = self.controller.db.read_circuit_data()
        else:
            results = self.controller.db.search_circuits(query)
        self.show_results(results)

    def remove_search(self):
        self.search_field.delete(0, tk.END)
        self.show_results(self.controller.db.read_circuit_data())
        