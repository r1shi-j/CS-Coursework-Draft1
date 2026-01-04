import platform

# creating a class called Fonts and creating static properties to use as font parameters
class Fonts:
    caption = ("TkDefaultFont", 10, "bold") # caption font which is smaller than standard but in bold
    base = ("TkDefaultFont", 11, "normal") # base is the standard font everywhere (11)
    base_u = ("TkDefaultFont", 11, "underline") # underline variant of base
    base_b = ("TkDefaultFont", 11, "bold") # bold version of base
    base2 = ("TkDefaultFont", 12, "normal") # base2 is the larger font (12)
    base2_b = ("TkDefaultFont", 12, "bold") # bold version of base2
    base2_i = ("TkDefaultFont", 12, "italic") # italic version of base2
    header = ("TkDefaultFont", 14, "bold") # header is used for the navigation headers (14)
    header_u = ("TkDefaultFont", 14, "bold underline") # underlined version of header used when hovering over a header
    tip = ("tahoma", 9, "normal") # used for text tip

# creating a class called Colours and defining a list of hex colours
class Colours:
    # these tuples are also used as the colours for buttons to open each statistic graph
    red = ("#ee7272","#e6241e") # delete, open login
    green = ("#5cdfa6","#32be94") # create, update/save, login, insert rr/gp results
    blue = ("#76BEFE","#279AFF") # next, open create tournament, open brackets
    dblue = ("#7b96f9","#2853c8") # open settings, open insert rr results
    purple = ("#C29CE5","#A165DA") # open create player
    gold = ("#FDC070","#EE9A2D") # open edit player
    gold_silver_bronze = ["#FFCC00", "#C0C0C0", "#CD7F32"] # defining bar colours for 1st, 2nd and 3rd places in stats
    logout = "#d05e5e" # logout
    winner = "#11DF11" # winner name
    hover = "#E5F1FB" # tournaments row background on hover
    cancel = "#8A9098" # cancel button
    back = "#695adb" # back button
    white = "#FFFFFF" # standard white colour
    black = "#000000" # standard black colour
    tip = "#ffffe0" # background for tip popovers
    disabled_bg = "#E0E0E0" # using for button background when disabled
    disabled_text = "#A0A0A0" # using for button text when disabled

    # different grey colours for macOS and Windows
    system = platform.system()
    # if os is Windows
    if system == "Windows":
        base_l = "#F0F0F0" # lighter colour to match TkLabelFrame colour but for windows its slightly darker grey
        base = "#E8E8E8" # standard grey colour but for windows its slightly darker grey
        base_d = "#DCDCDC" # setting a darker alternating frame colour for tournament list
        default_frame_bg = "#F0F0F0" # default background for windows is this hex on windows
        brackets_frame = "#F3F3F3" # setting the brackets background to this hex on macos
    else: # for macOS or Linux or other systems
        base_l = "#FAFAFA" # lighter colour to match TkLabelFrame colour
        base = "#F5F5F5" # standard grey colour
        base_d = "#DFDFDF" # darker alternating frame colour for tournament list
        default_frame_bg = white # default background for windows is white on macos
        brackets_frame = white # setting the brackets background to white on macos
