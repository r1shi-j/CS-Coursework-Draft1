import tkinter as tk

# Class to show a tip over a button
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

    def show_tip(self, event=None):
        # if tip is already being shown, or no text provided then do nothing
        if self.tip_window or not self.text:
            return

        # positioning the tip window with offsets from the original button
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 50
        y = y + self.widget.winfo_rooty() + 25
        
        # creating the tip window
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) 
        tw.wm_geometry("+%d+%d" % (x, y))
        
        # creating the label with custom background and font
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0", font=("tahoma", "9", "normal"))
        label.pack(ipadx=10, ipady=10)

    def hide_tip(self, event=None):
        # destroying the tip window
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()