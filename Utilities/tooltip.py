import tkinter as tk
from tkinter import ttk
from Utilities.animatedButton import AnimatedButton
from Utilities.FontStyling import Fonts as FS, Colours as FC
# importing relevant tkinter packages
# importing animatedButton to use as type in function below
# importing custom font styling to use for tip window text

# function to create a tip over a widget
def create_tooltip(widget: AnimatedButton | ttk.Label, text: str):
    toolTip = ToolTip(widget, text)
    # binding enter and leave hover events to show and hide the tip
    # add="+" allows to use existing bindings to the widget
    widget.bind("<Enter>", toolTip.show_tip, add="+")
    widget.bind("<Leave>", toolTip.hide_tip, add="+")

# class to show a tip over a button
class ToolTip:
    def __init__(self, widget: AnimatedButton | ttk.Label, text: str):
        self.widget = widget
        self.text = text
        self.tip_window = None

    def show_tip(self, event=None):
        # if tip is already being shown, or no text provided then do nothing
        if self.tip_window or not self.text:
            return
        
        # replacing spaces with _ in the circuit name
        filename = "_".join(self.text.split(" "))
        # making file path
        image_path = f"Mario Kart Images/{filename}_COVER Small.png"
        # trying to create image with the file path
        # fails if no photo at the path and so self.phote set to none
        try: self.photo = tk.PhotoImage(file=image_path)
        except: self.photo = None

        # positioning the tip window with offsets from the original button
        x = self.widget.winfo_rootx() + 80
        # if a photo is being shown then increase x by a further 20 because the image is large and don't want to hide rows below
        if self.photo: x += 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height()
        
        # creating the tip window
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) 
        tw.wm_geometry("+%d+%d" % (x, y))
        
        # if we are in statistics view showing tip over the button
        if type(self.widget) == AnimatedButton:
            # creating the label with custom background and font
            tk.Label(tw, text=self.text, justify=tk.LEFT, background=FC.tip, font=FS.tip).pack(ipadx=10, ipady=10)
        # else if we are in circuits view shoing tip over the circuit label
        else:
            # if there is an image then show it
            if self.photo:
                tk.Label(tw, image=self.photo).pack(pady=10)
            # if no image then the image couldn't be found
            else:
                # instead show a message that the Image wasn't found
                tk.Label(tw, text="Image not found", justify=tk.LEFT).pack(ipadx=10, ipady=7, pady=6)

    def hide_tip(self, event=None):
        # destroying the tip window
        tw = self.tip_window
        self.tip_window = None
        if tw: tw.destroy()