from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import pystray
from PIL import Image, ImageDraw
import threading
import json
import os

#install pystray pillow

DATA_FILE = os.path.join(os.path.dirname(__file__), "profiles.json")

# ---------------- Profile JSON ----------------
def load_profiles():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"active_profile" : None, "profiles" : {}}

def save_profiles(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

profiles_data = load_profiles()

# ---------------- Themes ----------------
THEMES = {
    "Default": {
        "bg": "#2c3e50",
        "fg": "white",
        "border_color": "#1f2a38",
    },
    "Dark": {
            "bg": "#1e1e1e",
            "fg": "#e0e0e0",
            "border_color": "#333333",
    },
    "Light": {
            "bg": "#f0f0f0",
            "fg": "#3a3a3a",
            "border_color": "#cccccc",
    },
    "Monokai": {
            "bg": "#272822",
            "fg": "#f8f8f2",
            "border_color": "#f92672",
    },
    "Nord": {
            "bg": "#2e3440",
            "fg": "#d8dee9",
            "border_color": "#88c0d0",
    },
    "Pastel": {
            "bg": "#fff8e7",
            "fg": "#5a5a5a",
            "border_color": "#ffd166",
    }
}


def apply_theme(widget=None):
    if widget is None:
        widget = root
    try:
        widget.configure(bg=current_theme["bg"])
    except Exception:
        pass
    try:
        widget.configure(fg=current_theme["fg"])
    except Exception:
        pass

    if widget == border_frame:
        try:
            widget.configure(bg=current_theme["border_color"])
        except Exception:
            pass
    for child in widget.winfo_children():
        apply_theme(child)

active_profile = profiles_data.get("active_profile")
if active_profile and active_profile in profiles_data["profiles"]:
    current_theme = THEMES[profiles_data["profiles"][active_profile]["theme"]]
else:
    current_theme = THEMES["Default"]

def load_dictionary_list():
    dictionaries_dir = os.path.join(os.path.dirname(__file__), "Dictionaries")
    if not os.path.exists(dictionaries_dir):
        os.makedirs(dictionaries_dir)
    dict_files = [f for f in os.listdir(dictionaries_dir) if f.endswith(".json")]
    return [os.path.splitext(f)[0] for f in dict_files]

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
#Remove Native OS Title Bar
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

# Icon Thread Listens For Clicks, Tray Thread Schedules Restores To Main Thread
icon = None
tray_thread = None
def create_icon():
    # Icon W/H and Icon Background Colors
    sprite = Image.new("RGB", (64,64), color=(46,64,90))
    d = ImageDraw.Draw(sprite)
    # Where Text Starts
    d.text((10, 20), "⌨️", fill=(255,255,255))
    return sprite

def restore_window(systray_icon=None, item=None):
    global icon
    def restore():
        # Unminimize, Top Of Windows, Keyboard Focus
        root.deiconify()
        root.lift()
        root.focus_force()
    # Schedules Restore To Main Thread
    root.after(0, restore)
    # Remove Icon From Tray
    if icon:
        icon.stop()
        icon = None

def quit_app(systray_icon=None, item=None):
    global icon
    # Remove Icon If Quit
    if icon:
        icon.stop()
    root.quit()

def setup_tray():
    global icon
    # Creates Icon, Allows Right Click Ability From Tray For Restore And Quit
    icon = pystray.Icon(
        "StenoApp",
        create_icon(),
        "Stenography Keyboard",
        menu=pystray.Menu(
            pystray.MenuItem("Restore", restore_window, default=True),
            pystray.MenuItem("Quit", quit_app)
        )
    )

    icon.run()

def minimize():
    global icon, tray_thread
    root.withdraw()
    if icon is None:
        tray_thread = threading.Thread(target=setup_tray, daemon=True)
        tray_thread.start()

# ---------------- Practice Box ----------------
practice_frame = Frame(main_frame, bg=current_theme["border_color"], bd=2)
practice_frame.place(
    x=20, y=150,
    width=window_width-40,
    height=window_height-200
)
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
top_bar = Frame(main_frame, bg=current_theme["bg"], height=50)
top_bar.pack(side="top", fill="x")

current_profile_frame = Frame(main_frame, bg=current_theme["bg"])
current_profile_frame.pack(side="top", fill="x", pady=(20,0))

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

current_dictionary_frame = Frame(main_frame, bg=current_theme["bg"])
current_dictionary_frame.pack(side="top", fill="x", pady=(10,0))

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

#Move Bar
def click_move(event):
    root.x = event.x
    root.y = event.y
def drag_move(event):
    x = event.x_root - root.x
    y = event.y_root - root.y
    root.geometry(f"+{x}+{y}")

#Bind Movement To Top Bar
top_bar.bind("<ButtonPress-1>", click_move)
top_bar.bind("<B1-Motion>", drag_move)

#Padx Aura
logo = Label(top_bar, text="⌨  Stenography Keyboard", bg=current_theme["bg"], fg=current_theme["fg"], font=("Arial", 20, "bold"))
logo.pack(side="left", padx=(0,30))

separator = ttk.Separator(top_bar, orient="vertical")
separator.pack(side="left", fill="y", padx=2)

profile_label = Label(top_bar, text="Profile:", bg=current_theme["bg"], fg=current_theme["fg"], font=("Calibri", 16, "bold"))
#Padx Left And Right
profile_label.pack(side="left", padx=(0,2))

# ---------------- Top Bar Widgets ----------------
def load_current_profile(name):
    current_profile_label.config(text=f"Current Profile: {name}")

def load_profile():
    global profiles_data
    if not profiles_data["profiles"]:
        messagebox.showwarning("No Profiles", "No Profiles Found, Please Create One Before Loading")
        return

    def load_choice():
        global current_theme
        choice = profile_var.get()
        if not choice:
            messagebox.showerror("Error", "No Profile Selected", parent=load_window)
            return
        profiles_data["active_profile"] = choice
        save_profiles(profiles_data)
        load_current_profile(choice)
        theme_name = profiles_data["profiles"][choice].get("theme", "Default")
        current_theme = THEMES[theme_name]
        apply_theme()
        dictionary_name = profiles_data["profiles"][choice].get("dictionary", "None")
        current_dictionary_label.config(text=f"Current Dictionary: {dictionary_name}")

        messagebox.showinfo("Profile Loaded", f"Now Using '{choice}'")
        load_window.destroy()

    load_window = Toplevel(root)
    load_window.title("Load Profile")
    load_window_width = 320
    load_window_height = 240
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    x = root_x + (root_width // 2) - (load_window_width // 2)
    y = root_y + (root_height // 2) - (load_window_height // 2)
    load_window.geometry(f"{load_window_width}x{load_window_height}+{x}+{y}")
    load_window.resizable(False, False)
    load_window.grab_set()

    Label(load_window, text="Select Profile:", font=("Calibri", 12)).pack(pady=(20,5))
    profile_var = StringVar()
    profile_dropdown = ttk.Combobox(
        load_window,
        textvariable=profile_var,
        values=list(profiles_data["profiles"].keys()),
        state="readonly"
    )
    profile_dropdown.pack(pady=5)
    active = profiles_data.get("active_profile")
    if active in profiles_data["profiles"]:
        profile_dropdown.set(active)
    else:
        profile_dropdown.set(list(profiles_data["profiles"].keys())[0])

    Button(load_window, text="Load Profile", command=load_choice).pack(pady=10)


def save_current_profile():
    global profiles_data
    if not profiles_data["active_profile"]:
        messagebox.showerror("Error", "No Profile Is Currently Active")
        return
    save_profiles(profiles_data)
    messagebox.showinfo("Success", f"Profile '{profiles_data['active_profile']}' Saved Successfully")

def new_profile():
    global profiles_data
    name = simpledialog.askstring("New Profile", "Enter Profile Name:")
    if not name:
        return
    if name in profiles_data["profiles"]:
        messagebox.showerror("Error", f"Profile '{name}' Already Exists")
        return
    profiles_data["profiles"][name] = {
        "theme": "Default",
        "dictionary": None,
        "custom_words": []
    }
    profiles_data["active_profile"] = name
    save_profiles(profiles_data)
    load_current_profile(name)
    messagebox.showinfo("Success", f"Profile '{name}' Created")

def edit_profile():
    global profiles_data
    if not profiles_data["profiles"]:
        messagebox.showwarning("No Profiles", "No Profiles Found To Edit")
        return

    dialog = Toplevel(root)
    dialog.title("Edit Profile")
    dialog_width = 320
    dialog_height = 240
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    x = root_x + (root_width // 2) - (dialog_width // 2)
    y = root_y + (root_height // 2) - (dialog_height // 2)
    dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    dialog.resizable(False, False)
    dialog.grab_set()


    Label(dialog, text="Select Profile", font=("Calibri", 14)).pack(pady=(20,5))
    profile_var = StringVar()
    profile_var.set(list(profiles_data["profiles"].keys())[0])
    profile_dropdown = ttk.Combobox(dialog, textvariable=profile_var, values=list(profiles_data["profiles"].keys()), state="readonly")
    profile_dropdown.pack(pady=5)

    button_frame = Frame(dialog)
    button_frame.pack(pady=20)

    def delete_action():
        prof = profile_var.get()
        confirm = messagebox.askyesno("Confirm Delete", f"Are You Sure You Want To Delete '{prof}'?")
        if confirm:
            if profiles_data["active_profile"] == prof:
                profiles_data["active_profile"] = None
                load_current_profile("None")
                current_dictionary_label.config(text=f"Current Dictionary: None")
            del profiles_data["profiles"][prof]
            save_profiles(profiles_data)
            messagebox.showinfo("Deleted", f"Profile '{prof}' Has Been Deleted")
            dialog.destroy()

    def rename_action():
        prof = profile_var.get()
        new_name = simpledialog.askstring("Rename Profile", f"Enter A New Name For Profile '{prof}'", parent=dialog)
        if not new_name:
            return
        if new_name in profiles_data["profiles"]:
            messagebox.showerror("Error", f"Profile '{new_name}' Already Exists", parent=dialog)
            return
        profiles_data["profiles"][new_name] = profiles_data["profiles"].pop(prof)
        if profiles_data["active_profile"] == prof:
            profiles_data["active_profile"] = new_name
            load_current_profile(new_name)
        save_profiles(profiles_data)
        messagebox.showinfo("Renamed", f"Profile '{prof}' Has Been Renamed To '{new_name}'")
        dialog.destroy()

    Button(button_frame, text="Rename", command=rename_action, width=10).pack(side="left", padx=10)
    Button(button_frame, text="Delete", command=delete_action, width=10).pack(side="right", padx=10)

if profiles_data["active_profile"]:
    load_current_profile(profiles_data["active_profile"])

new_profile_button = Button(top_bar, text="🆕 New", command=new_profile, bg=current_theme["bg"], fg=current_theme["fg"], bd=0, font=("Calibri", 16))
new_profile_button.pack(side="left", padx=2)

load_profile_button = Button(top_bar, text="📂 Load", command=load_profile, bg=current_theme["bg"], fg=current_theme["fg"], bd=0, font=("Calibri", 16))
load_profile_button.pack(side="left", padx=2)

edit_profile_button = Button(top_bar, text="🖊 Edit", command=edit_profile, bg=current_theme["bg"], fg=current_theme["fg"], bd=0, font=("Calibri", 16))
edit_profile_button.pack(side="left", padx=2)

save_profile_button = Button(top_bar, text="💾 Save", command=save_current_profile, bg=current_theme["bg"], fg=current_theme["fg"], bd=0, font=("Calibri", 16))
save_profile_button.pack(side="left", padx=2)


separator = ttk.Separator(top_bar, orient="vertical")
separator.pack(side="left", fill="y", padx=2)

dictionary_label = Label(top_bar, text="Dictionary:", bg=current_theme["bg"], fg=current_theme["fg"], font=("Calibri", 16, "bold"))
#Padx Left And Right
dictionary_label.pack(side="left", padx=(0,2))

#Border Width 0
import_dictionary_button = Button(top_bar, text="⬇ Import", bg=current_theme["bg"], fg=current_theme["fg"], bd=0, font=("Calibri", 16))
import_dictionary_button.pack(side="left", padx=2)

export_dictionary_button = Button(top_bar, text="⬆ Export", bg=current_theme["bg"], fg=current_theme["fg"], bd=0, font=("Calibri", 16))
export_dictionary_button.pack(side="left", padx=2)

separator = ttk.Separator(top_bar, orient="vertical")
separator.pack(side="left", fill="y", padx=2)


exit_button = Button(top_bar, text="❌", command=quit_app, bg=current_theme["bg"], fg=current_theme["fg"], bd=0)
exit_button.pack(side="right", padx=2)

minimize_button = Button(top_bar, text="━", command=minimize, bg=current_theme["bg"], fg=current_theme["fg"], bd=0)
minimize_button.pack(side="right", padx=2)

def show_settings():
    active_profile = profiles_data.get("active_profile")
    if not active_profile:
        messagebox.showerror("Error", "No Active Profile Selected")
        return

    settings_window = Toplevel(root)
    settings_window.title("Settings")
    window_width = 640
    window_height = 480
    settings_window.geometry(f"{window_width}x{window_height}")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    settings_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    settings_window.resizable(False, False)
    settings_window.configure(bg=current_theme["bg"])
    settings_window.attributes("-toolwindow", True)

    Label(settings_window, text=f"Profile: {profiles_data['active_profile']}", bg=current_theme["bg"], fg=current_theme["fg"], font=("Calibri", 14, "bold")).pack(pady=(30, 10))
    Label(settings_window, text="Theme:", bg=current_theme["bg"], fg=current_theme["fg"], font=("Calibri", 14, "bold")).pack(pady=(10,5))

    theme_var = StringVar()
    theme_var.set(profiles_data["profiles"][active_profile].get("theme", "Default"))

    theme_dropdown = ttk.Combobox(settings_window, textvariable=theme_var, state="readonly")
    theme_dropdown["values"] = list(THEMES.keys())
    theme_dropdown.pack(pady=5)


    Label(settings_window, text="Dictionary:", bg=current_theme["bg"], fg=current_theme["fg"], font=("Calibri", 14, "bold")).pack(pady=(10, 5))
    dictionary_var = StringVar()
    available_dictionaries = load_dictionary_list()
    dictionary_dropdown = ttk.Combobox(settings_window, textvariable=dictionary_var, state="readonly")
    dictionary_dropdown["values"] = available_dictionaries
    current_dict = profiles_data["profiles"][active_profile].get("dictionary")
    if current_dict in available_dictionaries:
        dictionary_var.set(current_dict)
    else:
        dictionary_var.set(available_dictionaries[0])
    dictionary_dropdown.pack(pady=5)

    def save_settings():
        global current_theme, current_dictionary_label
        profiles_data["profiles"][active_profile]["theme"] = theme_var.get()
        profiles_data["profiles"][active_profile]["dictionary"] = dictionary_var.get()
        save_profiles(profiles_data)

        current_theme = THEMES[theme_var.get()]
        apply_theme()

        current_dictionary_label.config(text=f"Current Dictionary: {dictionary_var.get()}")

        messagebox.showinfo("Settings Saved", f"Theme Is Now: '{theme_var.get()}' And Dictionary Is Now: '{dictionary_var.get()}'")

    save_button = Button(settings_window, text="Save Settings", command=save_settings, bg=current_theme["bg"], fg=current_theme["fg"], font=("Calibri", 12))
    save_button.pack(pady=20)


settings_button = Button(top_bar, text="⚙️", command=show_settings, bg=current_theme["bg"], fg=current_theme["fg"], bd=0)
settings_button.pack(side="right", padx=2)

def show_help():
    help_window = Toplevel(root)
    help_window.title("Help")
    window_width = 640
    window_height = 480
    # Screen Geometry Starting Position
    help_window.geometry(f"{window_width}x{window_height}")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    help_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    help_window.resizable(False, False)
    help_window.configure(bg=current_theme["bg"])
    help_window.attributes("-toolwindow", True)

    Label(help_window, text="Help Menu", bg=current_theme["bg"], fg=current_theme["fg"], font=("Arial", 18, "bold")).pack(pady=10)
    Label(help_window, text="To Close The Program, Press ❌", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)
    Label(help_window, text="To Minimize The Program, Press ━", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)
    Label(help_window, text="To Access Your Settings, Press ⚙️", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)
    Label(help_window, text="To Create A New Profile, Select New", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)
    Label(help_window, text="To Load A Profile, Select Load", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)
    Label(help_window, text="To Edit A Profile, Select Edit", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)
    Label(help_window, text="To Save Profile Changes, Select Save", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)
    Label(help_window, text="To Import A Dictionary, Select Import", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)
    Label(help_window, text="To Export A Dictionary, Select Export", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)


help_button = Button(top_bar, text="❓", command=show_help, bg=current_theme["bg"], fg=current_theme["fg"], bd=0)
help_button.pack(side="right", padx=2)


root.mainloop()