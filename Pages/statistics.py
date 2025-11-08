import tkinter as tk
from tkinter import ttk

class StatisticsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Statistics Page", font=("TkDefaultFont", 14)).pack(pady=20)

    def load_player_stats(self, player):
        print("player loaded in statistics page:", player)

    def load_circuit_stats(self, circuit):
        print("circuit loaded in statistics page:", circuit)