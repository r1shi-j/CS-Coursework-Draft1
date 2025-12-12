import tkinter as tk
from tkinter import ttk

# function to create a tip over a widget
def create_tooltip(widget: ttk.Button | ttk.Label, text: str, is_stats: bool):
    # creating the tip
    # binding enter and leave events to show and hide the tip
    toolTip = ToolTip(widget, text, is_stats)
    widget.bind("<Enter>", toolTip.show_tip)
    widget.bind("<Leave>", toolTip.hide_tip)

# Class to show a tip over a button
class ToolTip:
    def __init__(self, widget: ttk.Button | ttk.Label, text: str, is_stats: bool):
        self.widget = widget
        self.text = text
        self.is_stats = is_stats
        self.tip_window = None

    def show_tip(self, event=None):
        # if tip is already being shown, or no text provided then do nothing
        if self.tip_window or not self.text:
            return

        # positioning the tip window with offsets from the original button
        x = self.widget.winfo_rootx() + 50
        if not self.is_stats: x += 50
        y = self.widget.winfo_rooty() + self.widget.winfo_height()
        
        # creating the tip window
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) 
        tw.wm_geometry("+%d+%d" % (x, y))
        
        if self.is_stats:
            # creating the label with custom background and font
            label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0", font=("tahoma", "9", "normal"))
            label.pack(ipadx=10, ipady=10)
            # adding the hover
            self.widget.config(style="Hover.TButton")
        else:
            # show image
            filename = "_".join(self.text.split(" "))
            image_path = f"Mario Kart Images/{filename}_COVER Small.png"
            # trying to show the image
            try:
                self.photo = tk.PhotoImage(file=image_path)
                label = tk.Label(tw, image=self.photo)
                label.pack(pady=10)
            except:
                # fails because image isn't in assets
                tk.Label(tw, text="Image not found").pack(pady=15, padx=8)

            # adding the hover
            self.widget.config(font=("TkDefaultFont", 10, "underline"))

    def hide_tip(self, event=None):
        # destroying the tip window
        tw = self.tip_window
        self.tip_window = None
        if tw: tw.destroy()
        # removing the underline when unhover
        if self.is_stats: self.widget.config(style="UnHover.TButton")
        else: self.widget.config(font=("TkDefaultFont", 10, "normal"))