import tkinter as tk
from tkinter import ttk

class StatisticsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        ttk.Label(self, text="Statistics Page", font=("Arial", 14)).pack(pady=20)