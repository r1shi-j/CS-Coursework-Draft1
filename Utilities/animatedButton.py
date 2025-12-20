import tkinter as tk
from Utilities.FontStyling import Fonts as FS, Colours as FC
# importing tkinter
# importing FontStyling to get custom fonts and colours

# declaring a constant default cursor
DEFAULT_CURSOR = "arrow"

# function to convert a hex colour to an rgb colour
def hex_to_rgb(hex_val: str):
    return tuple(int(hex_val.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

# helper function to find the middle colour hex between 2 hex colours
def interpolate_colour(start_hex: str, end_hex: str, progress: float):
    # first convert the start and end to rgb
    start_rgb = hex_to_rgb(start_hex)
    end_rgb = hex_to_rgb(end_hex)
    # math formula to find the middle hex in terms of colour
    new_rgb = tuple(int(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * progress) for i in range(3))
    # converting back to hex
    return '#{:02x}{:02x}{:02x}'.format(*new_rgb)

# custom button class
class AnimatedButton(tk.Canvas):
    # initialiser with all parameters
    def __init__(self, parent, text:str, command, 
                 width:int=120, height:int=34, corner_radius:int=16,
                 base_colour:str=FC.base, hover_colour:str="", text_colour:str=FC.black, font:tuple[str,int,str]=FS.base,
                 hover_cursor:str=DEFAULT_CURSOR, frame_colour:str|None=None, rounded_corners:list[str]|None=None):
        
        # if a frame colour is passed in then set it to the parent_bg variable
        if frame_colour:
            parent_bg = frame_colour
        else:
            # otherwise use the default frame background colour in FontStyling file
            # which is white it macos otherwise a light grey if windows
            parent_bg = FC.default_frame_bg
        
        # the tk.Canvas initialiser
        super().__init__(parent, width=width, height=height, bg=parent_bg, highlightthickness=0)
        
        # setting variables from function arguments
        self.command = command
        self.base_colour = base_colour
        self.hover_colour = hover_colour
        self.current_colour = base_colour
        self.hover_cursor = hover_cursor
        self.text_colour = text_colour
        self.is_disabled = False 
        
        # default to all corners rounded if not specified
        if rounded_corners is None:
            rounded_corners = ["top_left", "top_right", "bottom_left", "bottom_right"]
            
        self.shapes = []
        d = corner_radius * 2 # diameter
        r = corner_radius # radius
        
        # inbuilt function that creates a rectangle on the canvas
        # creating the middle rectangle
        self.shapes.append(self.create_rectangle(r, 0, width-r, height, fill=base_colour, outline=""))
        self.shapes.append(self.create_rectangle(0, r, width, height-r, fill=base_colour, outline=""))
        
        # creating the corners
        # if the corner is in rounded_corners then create an oval, otherwise create a rectangle
        # for rounded corners: using width and d to calculate the x values, height and d for y values
        # for square corners: using r instead of d for above

        if "top_left" in rounded_corners:
            self.shapes.append(self.create_oval(0, 0, d, d, fill=base_colour, outline=""))
        else:
            self.shapes.append(self.create_rectangle(0, 0, r, r, fill=base_colour, outline=""))

        if "top_right" in rounded_corners:
            self.shapes.append(self.create_oval(width-d, 0, width, d, fill=base_colour, outline=""))
        else:
            self.shapes.append(self.create_rectangle(width-r, 0, width, r, fill=base_colour, outline=""))

        if "bottom_left" in rounded_corners:
            self.shapes.append(self.create_oval(0, height-d, d, height, fill=base_colour, outline=""))
        else:
            self.shapes.append(self.create_rectangle(0, height-r, r, height, fill=base_colour, outline=""))

        if "bottom_right" in rounded_corners:
            self.shapes.append(self.create_oval(width-d, height-d, width, height, fill=base_colour, outline=""))
        else:
            self.shapes.append(self.create_rectangle(width-r, height-r, width, height, fill=base_colour, outline=""))
        
        # drawing text in the middle of the view
        self.text_id = self.create_text(width/2, height/2, text=text, fill=text_colour, font=font)
        
        # binding hover and click events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        # animation steps
        self.animation_step = 0
        self.total_steps = 25
        self.animating = False

    # function to changed button state
    def set_state(self, state):
        # if new state is disabled
        if state == "disabled":
            # set disabled property to true
            self.is_disabled = True
            # set cursor to default
            self.config(cursor=DEFAULT_CURSOR)
            # making background grey
            for shape in self.shapes:
                self.itemconfig(shape, fill=FC.disabled_bg)
            # making text colour grey
            self.itemconfig(self.text_id, fill=FC.disabled_text)
            
        elif state == "normal":
            # set disabled property to false
            self.is_disabled = False
            # reset cursor to original
            self.config(cursor=self.hover_cursor)
            # resetting the current colour to the original
            self.current_colour = self.base_colour
            # setting background back to original
            for shape in self.shapes:
                self.itemconfig(shape, fill=self.base_colour)
            # setting text colour back to original
            self.itemconfig(self.text_id, fill=self.text_colour)

    # function that runs on hover
    def on_enter(self, event):
        # if button is disabled then don't to anything
        if self.is_disabled:
            return
        # start animation with end colour of the hover colour
        self.start_animation(self.hover_colour)
        # changing the font colour from black to white
        self.itemconfig(self.text_id, fill=FC.white) 
        # changing the cursor
        self.config(cursor=self.hover_cursor)

    # function that runs when unhover
    def on_leave(self, event):
        # if button is disabled then don't do anything
        if self.is_disabled:
            return
        # start animation with end colour of the unhover colour
        self.start_animation(self.base_colour)
        # changing the font colour from white to black
        self.itemconfig(self.text_id, fill=FC.black)
        # changing the cursor back to standard
        self.config(cursor=DEFAULT_CURSOR)

    # function that runs on button click
    def on_click(self, event):
        # if button is disabled don't do anything
        if self.is_disabled:
            return
        # if there is a command passed in function then run it
        if self.command:
            self.command()

    # function that starts the animation taking in parameter for the target colour
    def start_animation(self, target_hex: str):
        # changing the global target colour
        self.target_colour = target_hex
        # setting the start colour
        self.start_hex = self.current_colour
        # resetting the current animation step to 0
        self.animation_step = 0
        
        # if not currently animating then start animating
        if not self.animating:
            self.animate_loop()

    # function that animates the colour change
    def animate_loop(self):
        # set animating status to true
        self.animating = True
        # increment the current animation step
        self.animation_step += 1
        
        # calculate the current animation progress
        progress = self.animation_step / self.total_steps
        
        # calculate new colour
        new_colour = interpolate_colour(self.start_hex, self.target_colour, progress)
        
        # update all shape backgrounds
        for shape_id in self.shapes:
            self.itemconfig(shape_id, fill=new_colour)
            
        self.current_colour = new_colour 
        
        # recursive step
        # if not finished: the current step is lower than the total steps then call function
        if self.animation_step < self.total_steps:
            # call again in 10ms (approx 100fps attempts)
            self.after(10, self.animate_loop)
        else:
            # if final step then exit recursion loop
            # set animating status to false
            self.animating = False