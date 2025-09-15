import tkinter as tk
from tkinter import ttk

class TournamentsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ttk.Label(self, text="Tournaments Page", font=("Arial", 14)).pack(pady=20)

        self.build_view()

    def build_view(self):
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

        results = self.controller.db.read_tournament_data()
        for row in results:
            row_frame = ttk.Frame(self.results_frame)
            row_frame.pack(fill="x", pady=2)

            winner = self.controller.db.find_tournament_winner(row[0])
            if winner != []:
                ttk.Label(row_frame, text=winner[0][1], width=20, anchor="w").pack(side="left")
                
            ttk.Label(row_frame, text=row[1], width=20, anchor="w").pack(side="left")
