import tkinter as tk
from tkinter import ttk
from Utilities.animatedButton import AnimatedButton
from Utilities.FontStyling import Fonts as FS, Colours as FC
# importing relevant tkinter packages
# importing animatedButton to use as type in function below
# importing custom font styling to use for tip window text

# function to create a tip over a widget
def create_tooltip(widget: AnimatedButton | ttk.Label, text: str, is_stats: bool):
    toolTip = ToolTip(widget, text, is_stats)
    # binding enter and leave hover events to show and hide the tip
    # add="+" allows to use existing bindings to the widget
    widget.bind("<Enter>", toolTip.show_tip, add="+")
    widget.bind("<Leave>", toolTip.hide_tip, add="+")

# Class to show a tip over a button
class ToolTip:
    def __init__(self, widget: AnimatedButton | ttk.Label, text: str, is_stats: bool):
        self.widget = widget
        self.text = text
        self.is_stats = is_stats
        self.tip_window = None

    def show_tip(self, event=None):
        # if tip is already being shown, or no text provided then do nothing
        if self.tip_window or not self.text:
            return

        # positioning the tip window with offsets from the original button
        x = self.widget.winfo_rootx() + 80
        # if tip is being shown from circuits then increase x by a further 20 because the image is large and don't want to hide rows below
        if not self.is_stats: x += 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height()
        
        # creating the tip window
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) 
        tw.wm_geometry("+%d+%d" % (x, y))
        
        if self.is_stats:
            # creating the label with custom background and font
            label = tk.Label(tw, text=self.text, justify=tk.LEFT, background=FC.tip, font=FS.tip)
            label.pack(ipadx=10, ipady=10)
        else:
            # replacing spaces with _ in the circuit name
            filename = "_".join(self.text.split(" "))
            # making file path
            image_path = f"Mario Kart Images/{filename}_COVER Small.png"
            # trying to show the image
            try:
                self.photo = tk.PhotoImage(file=image_path)
                label = tk.Label(tw, image=self.photo)
                label.pack(pady=10)
            except:
                # fails because image isn't in assets
                tk.Label(tw, text="Image not found").pack(pady=15, padx=8)

    def hide_tip(self, event=None):
        # destroying the tip window
        tw = self.tip_window
        self.tip_window = None
        if tw: tw.destroy()