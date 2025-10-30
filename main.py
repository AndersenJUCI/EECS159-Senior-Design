from tkinter import *

import gui.themes as themes
import gui.tray as tray
import gui.widgets as widgets
import gui.widget_helpers as helpers

# install pystray pillow

# ---------------- Profile JSON ----------------

profiles_data = helpers.profiles_data

active_profile = profiles_data.get("active_profile")
if active_profile and active_profile in profiles_data["profiles"]:
    current_theme = themes.get_theme(profiles_data["profiles"][active_profile].get("theme", "Default"))
else:
    current_theme = themes.get_theme("Default")


# ---------------- Base Window ----------------
root = Tk()
root.title("Stenography Keyboard")
window_width = 1280
window_height = 720
# Screen Geometry Starting Position
root.geometry(f"{window_width}x{window_height}")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

root.resizable(False, False)
root.configure(bg=current_theme["bg"])
# Remove Native OS Title Bar
root.overrideredirect(True)

# ---------------- Border ----------------
border_thickness = 5
border_frame = Frame(root, bg=current_theme["border_color"])
border_frame.place(x=0, y=0, relwidth=1, relheight=1)
main_frame = Frame(border_frame, bg=current_theme["bg"])
main_frame.place(x=border_thickness,y=border_thickness,
                 width=window_width-border_thickness*2,
                 height=window_height-border_thickness*2)

# ---------------- System Tray ----------------
helpers.root = root
helpers.current_theme = current_theme
helpers.border_frame = border_frame
system_tray = tray.SystemTray(root)
top_bar = widgets.main_bar(root, main_frame, system_tray, {"bg":current_theme["bg"], "fg":current_theme["fg"], "border_color":current_theme["border_color"]}, border_frame)

# ---------------- Practice Box (Eventually It's Own Window) ----------------
practice_frame = Frame(
    main_frame,
    bg=current_theme["bg"],
    highlightbackground=current_theme["border_color"],
    highlightthickness=2
)
practice_frame.place(x=20, y=150, width=window_width-40, height=window_height-200)

text_box = Text(
    practice_frame,
    bg=current_theme["bg"],
    fg=current_theme["fg"],
    insertbackground=current_theme["fg"],
    font=("Calibri", 16),
    wrap="word",
    bd=0,
    highlightthickness=0,
    padx=10,
    pady=10
)
text_box.pack(fill="both", expand=True)

# ---------------- Top Bar ----------------

current_profile_frame = Frame(
    main_frame,
    bg=current_theme["bg"]
)
current_profile_frame.pack(side="top", fill="x", pady=(20, 0))

current_profile_label = Label(
    current_profile_frame,
    text="Current Profile: None",
    bg=current_theme["bg"],
    fg="white",
    font=("Calibri", 16, "bold"),
    anchor="w",
    padx=10
)
current_profile_label.pack(fill="x")

current_dictionary_frame = Frame(
    main_frame,
    bg=current_theme["bg"]
)
current_dictionary_frame.pack(side="top", fill="x", pady=(10, 0))

current_dictionary_label = Label(
    current_dictionary_frame,
    text="Current Dictionary: None",
    bg=current_theme["bg"],
    fg="white",
    font=("Calibri", 16, "bold"),
    anchor="w",
    padx=10
)
current_dictionary_label.pack(fill="x")

helpers.set_labels(current_profile_label, current_dictionary_label)

# Move Bar
def click_move(event):
    root.x = event.x
    root.y = event.y
def drag_move(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f"+{x}+{y}")


# Bind Movement To Top Bar
top_bar.bind("<ButtonPress-1>", click_move)
top_bar.bind("<B1-Motion>", drag_move)

# ---------------- Top Bar Widgets ----------------


if profiles_data["active_profile"]:
    helpers.load_current_profile(profiles_data["active_profile"])

root.mainloop()