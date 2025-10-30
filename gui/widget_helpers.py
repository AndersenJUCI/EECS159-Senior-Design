from tkinter import *
from tkinter import messagebox, simpledialog, ttk
import gui.themes as themes
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
PROFILE_PATH = os.path.join(ROOT_DIR, "profiles.json")

current_profile_label = None
current_dictionary_label = None
root = None
current_theme = None
border_frame = None

def load_profiles():
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r") as f:
            return json.load(f)
    return {"active_profile" : None, "profiles" : {}}


profiles_data = load_profiles()

def set_labels(profile_label, dictionary_label):
    global current_profile_label, current_dictionary_label
    current_profile_label = profile_label
    current_dictionary_label = dictionary_label

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
        current_theme = themes.get_theme(theme_name)
        themes.apply_theme(root, current_theme, border_frame=border_frame)
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

def show_settings():
    global current_theme
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
    theme_dropdown["values"] = list(themes.THEMES.keys())
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
        global current_dictionary_label
        profiles_data["profiles"][active_profile]["theme"] = theme_var.get()
        profiles_data["profiles"][active_profile]["dictionary"] = dictionary_var.get()
        save_profiles(profiles_data)

        current_theme = themes.get_theme(theme_var.get())
        themes.apply_theme(root, current_theme, border_frame=border_frame)

        current_dictionary_label.config(text=f"Current Dictionary: {dictionary_var.get()}")

        messagebox.showinfo("Settings Saved", f"Theme Is Now: '{theme_var.get()}' And Dictionary Is Now: '{dictionary_var.get()}'")

    save_button = Button(settings_window, text="Save Settings", command=save_settings, bg=current_theme["bg"], fg=current_theme["fg"], font=("Calibri", 12))
    save_button.pack(pady=20)

def show_help():
    global current_theme
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

def save_profiles(data):
    with open(PROFILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

def load_dictionary_list():
    dictionaries_dir = os.path.join(ROOT_DIR, "Dictionaries")
    if not os.path.exists(dictionaries_dir):
        os.makedirs(dictionaries_dir)
    dict_files = [f for f in os.listdir(dictionaries_dir) if f.endswith(".json")]
    return [os.path.splitext(f)[0] for f in dict_files]