from tkinter import *
from tkinter import messagebox, simpledialog, ttk, filedialog
import gui.themes as themes
import shutil
import translation.translate as trans
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
        if dictionary_name and dictionary_name != "None":
            trans.load_active(dictionary_name)
            trans.reset_strokes()

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

    Label(dialog, text="Select Profile", font=("Calibri", 12)).pack(pady=(20,5))
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
        global current_theme, current_dictionary_label
        profiles_data["profiles"][active_profile]["theme"] = theme_var.get()
        profiles_data["profiles"][active_profile]["dictionary"] = dictionary_var.get()
        save_profiles(profiles_data)

        current_theme = themes.get_theme(theme_var.get())
        themes.apply_theme(root, current_theme, border_frame=border_frame)

        current_dictionary_label.config(text=f"Current Dictionary: {dictionary_var.get()}")

        if dictionary_var.get() and dictionary_var.get() != "None":
            trans.load_active(dictionary_var.get())
            trans.reset_strokes()

        messagebox.showinfo(
            "Settings Saved",
            f"Theme Is Now: '{theme_var.get()}' And Dictionary Is Now: '{dictionary_var.get()}'"
        )

    add_word_button = Button(settings_window, text="Add Word", command=add_word, bg=current_theme["bg"], fg=current_theme["fg"], font=("Calibri", 12))
    add_word_button.pack(pady=(20, 10))

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
    Label(help_window, text="To Attempt Practice Lessons, Select Practice Tool", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)
    Label(help_window, text="To Turn On Translation Mode, Select Translation", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)
    Label(help_window, text="To Find A Word's Translation, Select Lookup Word", bg=current_theme["bg"], fg=current_theme["fg"]).pack(anchor="w", padx=10)

def save_profiles(data):
    with open(PROFILE_PATH, "w") as f:
        json.dump(data, f, indent=4)

def load_dictionary_list():
    dictionaries_dir = os.path.join(ROOT_DIR, "Dictionaries")
    if not os.path.exists(dictionaries_dir):
        os.makedirs(dictionaries_dir)
    dict_files = [f for f in os.listdir(dictionaries_dir) if f.endswith(".json")]
    return [os.path.splitext(f)[0] for f in dict_files]

def lookup_word():
    active_profile = profiles_data.get("active_profile")
    if not active_profile:
        messagebox.showerror("Error", "No active profile selected.")
        return

    dictionary_name = profiles_data["profiles"][active_profile].get("dictionary")
    if not dictionary_name:
        messagebox.showerror("Error", "No dictionary is assigned to the active profile.")
        return

    dictionary_path = os.path.join(ROOT_DIR, "Dictionaries", f"{dictionary_name}.json")
    if not os.path.exists(dictionary_path):
        messagebox.showerror("Error", f"Dictionary '{dictionary_name}' was not found.")
        return

    try:
        with open(dictionary_path, "r", encoding="utf-8") as f:
            dictionary_data = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load dictionary.\n\n{e}")
        return

    lookup = Toplevel(root)
    lookup.title("Lookup Word")
    lookup_width = 480
    lookup_height = 360

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    x = root_x + (root_width // 2) - (lookup_width // 2)
    y = root_y + (root_height // 2) - (lookup_height // 2)

    lookup.geometry(f"{lookup_width}x{lookup_height}+{x}+{y}")
    lookup.resizable(False, False)
    lookup.grab_set()
    lookup.configure(bg=current_theme["bg"])

    Label(lookup, text="Type the word you'd like the translation for", font=("Calibri", 14), bg=current_theme["bg"], fg=current_theme["fg"]).pack(pady=(20, 10))

    word_var = StringVar()

    entry = Entry(lookup, textvariable=word_var, font=("Calibri", 14), width=25)
    entry.pack(pady=10)
    entry.focus_set()

    result_label = Label(lookup, text="Translation: ", font=("Calibri", 14, "bold"), bg=current_theme["bg"], fg=current_theme["fg"], wraplength=420, justify="left")
    result_label.pack(pady=20)

    def search_word():
        target_word = word_var.get().strip().lower()
        if not target_word:
            result_label.config(text="Translation: Please enter a word.")
            return

        matches = [outline for outline, word in dictionary_data.items() if word.lower() == target_word]

        if matches:
            result_label.config(text=f"Translation: {', '.join(matches)}")
        else:
            result_label.config(text="Translation: Word not found in current dictionary.")

    Button(lookup, text="Search", command=search_word, font=("Calibri", 12), width=12).pack(pady=10)

    entry.bind("<Return>", lambda event: search_word())

def export_dictionary():
    available_dictionaries = load_dictionary_list()

    if not available_dictionaries:
        messagebox.showwarning("No Dictionaries", "No dictionaries were found to export.")
        return

    export_window = Toplevel(root)
    export_window.title("Export Dictionary")
    export_width = 360
    export_height = 180

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    x = root_x + (root_width // 2) - (export_width // 2)
    y = root_y + (root_height // 2) - (export_height // 2)

    export_window.geometry(f"{export_width}x{export_height}+{x}+{y}")
    export_window.resizable(False, False)
    export_window.grab_set()

    Label(export_window, text="Select Dictionary To Export", font=("Calibri", 12)).pack(pady=(20, 10))

    dictionary_var = StringVar()
    dictionary_dropdown = ttk.Combobox(
        export_window,
        textvariable=dictionary_var,
        values=available_dictionaries,
        state="readonly"
    )
    dictionary_dropdown.pack(pady=5)
    dictionary_dropdown.set(available_dictionaries[0])

    def confirm_export():
        dictionary_name = dictionary_var.get()
        if not dictionary_name:
            messagebox.showerror("Error", "No dictionary selected.", parent=export_window)
            return

        source_path = os.path.join(ROOT_DIR, "Dictionaries", f"{dictionary_name}.json")

        save_path = filedialog.asksaveasfilename(
            parent=export_window,
            title="Save Dictionary As",
            defaultextension=".json",
            initialfile=f"{dictionary_name}.json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not save_path:
            return

        try:
            shutil.copyfile(source_path, save_path)
            messagebox.showinfo("Export Complete", f"Dictionary '{dictionary_name}' exported successfully.")
            export_window.destroy()
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export dictionary.\n\n{e}", parent=export_window)

    Button(export_window, text="Export", command=confirm_export, width=12).pack(pady=15)

def import_dictionary():
    dictionaries_dir = os.path.join(ROOT_DIR, "Dictionaries")
    if not os.path.exists(dictionaries_dir):
        os.makedirs(dictionaries_dir)

    file_path = filedialog.askopenfilename(
        parent=root,
        title="Select Dictionary File",
        filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
    )

    if not file_path:
        return

    file_name = os.path.basename(file_path)
    destination_path = os.path.join(dictionaries_dir, file_name)

    if os.path.abspath(file_path) == os.path.abspath(destination_path):
        messagebox.showinfo("Import Skipped", "That dictionary is already in the Dictionaries folder.")
        return

    if os.path.exists(destination_path):
        overwrite = messagebox.askyesno(
            "Replace Dictionary",
            f"'{file_name}' already exists. Do you want to replace it?"
        )
        if not overwrite:
            return

    try:
        shutil.copyfile(file_path, destination_path)
        messagebox.showinfo("Import Complete", f"Dictionary '{os.path.splitext(file_name)[0]}' imported successfully.")
    except Exception as e:
        messagebox.showerror("Import Failed", f"Could not import dictionary.\n\n{e}")


def add_word():
    active_profile = profiles_data.get("active_profile")
    if not active_profile:
        messagebox.showerror("Error", "No active profile selected.")
        return

    dictionary_name = profiles_data["profiles"][active_profile].get("dictionary")
    if not dictionary_name or dictionary_name == "None":
        messagebox.showerror("Error", "No active dictionary selected.")
        return

    dictionary_path = os.path.join(ROOT_DIR, "Dictionaries", f"{dictionary_name}.json")
    if not os.path.exists(dictionary_path):
        messagebox.showerror("Error", f"Dictionary '{dictionary_name}' was not found.")
        return

    try:
        with open(dictionary_path, "r", encoding="utf-8") as f:
            dictionary_data = json.load(f)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load dictionary.\n\n{e}")
        return

    add_window = Toplevel(root)
    add_window.title("Add Word")
    add_width = 500
    add_height = 320

    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    x = root_x + (root_width // 2) - (add_width // 2)
    y = root_y + (root_height // 2) - (add_height // 2)

    add_window.geometry(f"{add_width}x{add_height}+{x}+{y}")
    add_window.resizable(False, False)
    add_window.grab_set()
    add_window.configure(bg=current_theme["bg"])

    Label(
        add_window,
        text=f"Adding to dictionary: {dictionary_name}",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 14, "bold")
    ).pack(pady=(20, 15))

    Label(
        add_window,
        text="Word:",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 12, "bold")
    ).pack()

    word_var = StringVar()
    word_entry = Entry(add_window, textvariable=word_var, font=("Calibri", 12), width=30)
    word_entry.pack(pady=(5, 15))

    Label(
        add_window,
        text="Chord / Translation:",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 12, "bold")
    ).pack()

    chord_var = StringVar()
    chord_entry = Entry(add_window, textvariable=chord_var, font=("Calibri", 12), width=30)
    chord_entry.pack(pady=(5, 10))

    status_label = Label(
        add_window,
        text="",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 11),
        wraplength=420,
        justify="left"
    )
    status_label.pack(pady=(10, 15))

    def check_chord():
        chord = chord_var.get().strip().upper()
        if not chord:
            status_label.config(text="Please enter a chord to check.", fg="orange")
            return False

        if chord in dictionary_data:
            status_label.config(
                text=f"That chord is already used for '{dictionary_data[chord]}'. Please choose another.",
                fg="red"
            )
            return False

        status_label.config(text="Chord is available.", fg="lime")
        return True

    def submit_word():
        word = word_var.get().strip()
        chord = chord_var.get().strip().upper()

        if not word or not chord:
            messagebox.showerror("Error", "Both word and chord are required.", parent=add_window)
            return

        if chord in dictionary_data:
            messagebox.showerror(
                "Error",
                f"That chord is already used for '{dictionary_data[chord]}'. Please choose another.",
                parent=add_window
            )
            return

        dictionary_data[chord] = word

        try:
            with open(dictionary_path, "w", encoding="utf-8") as f:
                json.dump(dictionary_data, f, indent=4)
            messagebox.showinfo("Success", f"Added '{word}' with chord '{chord}' to {dictionary_name}.", parent=add_window)
            add_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save dictionary.\n\n{e}", parent=add_window)

    button_frame = Frame(add_window, bg=current_theme["bg"])
    button_frame.pack(pady=10)

    Button(
        button_frame,
        text="Check Chord",
        command=check_chord,
        font=("Calibri", 11),
        width=12
    ).pack(side="left", padx=10)

    Button(
        button_frame,
        text="Submit",
        command=submit_word,
        font=("Calibri", 11),
        width=12
    ).pack(side="left", padx=10)

def show_practice():
    global current_theme
    practice_window = Toplevel(root)
    practice_window.title("Practice")
    window_width = 800
    window_height = 600
    # Screen Geometry Starting Position
    practice_window.geometry(f"{window_width}x{window_height}")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    practice_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    practice_window.resizable(False, False)
    practice_window.configure(bg=current_theme["bg"])
    practice_window.attributes("-toolwindow", True)

    tutorials = ("Tutorial 1: Your First Word",
                 "Tutorial 2: Double Chord Word",
                 "Tutorial 3: Multi-Chord Word",
                 "Tutorial 4: Change",
                 "Tutorial 5: Change",
                 "Tutorial 6: Change",
                 "Tutorial 7: Change",
                 "Tutorial 8: Change",
                 )

    tutorials_instructions = ("Write the word 'why' by pressing the keys K-W-R simultaneously",
                              "Tutorial 2: Write the word 'boredom' by pressing the keys P-W-O-R followed by T-K-O-P-L",
                              "Tutorial 3: Write the word 'popularity' by pressing the keys P-O-P/K-W-R-U/H-R-A-R/T-E-U",
                              "Tutorial 4: Change",
                              "Tutorial 5: Change",
                              "Tutorial 6: Change",
                              "Tutorial 7: Change",
                              "Tutorial 8: Change",

                 )

    list_frame = Frame(practice_window, bg=current_theme["bg"], width=200)
    list_frame.pack(side="left", fill="y", padx=10, pady=10)

    Label(list_frame, text="Tutorials", bg=current_theme["bg"], fg=current_theme["fg"],
          font=("Calibri", 14, "bold")).pack(pady=(0, 2))

    list_border = Frame(list_frame, bg=current_theme["border_color"], bd=0)
    list_border.pack(fill="both", expand=True, padx=4, pady=4)

    text_frame = Frame(practice_window, bg=current_theme["bg"])
    text_frame.pack(side="right", fill="both", padx=10, pady=10)

    instruction_label = Label(text_frame, text="Lesson: ", bg=current_theme["bg"], fg=current_theme["fg"], wraplength=550, justify="left",
          font=("Calibri", 14, "bold"))
    instruction_label.pack(anchor="nw", pady=(0, 50))

    practice_button_frame = Frame(text_frame, bg=current_theme["bg"], bd=0)
    practice_button_frame.pack(side="bottom", fill="x", pady=10)

    text_border = Frame(text_frame, bg=current_theme["border_color"], bd=0)
    text_border.pack(fill="both", padx=4, pady=4)

    tutorial_list = Listbox(list_border, bg=current_theme["bg"], fg=current_theme["fg"], bd=0, highlightthickness=0, width=30, font=("Calibri", 12,))
    for i in tutorials:
        tutorial_list.insert(END, i)

    tutorial_list.pack(fill="y", expand=True, padx=2, pady=2)

    text_box = Text(text_border, bg=current_theme["bg"], fg=current_theme["fg"], height=30, font=("Calibri", 12), bd=0, highlightthickness=0)
    text_box.pack(fill="both", padx=2, pady=2)

    def update_instruction():
        selected_lesson = tutorial_list.curselection()
        if selected_lesson:
            index = selected_lesson[0]
            instruction_label.config(text="Lesson: " + tutorials_instructions[index])

    begin_button = Button(practice_button_frame, text="Select Lesson", command=update_instruction, width=12, font=("Calibri", 14))
    begin_button.pack(side="left", padx=20)
    restart_button = Button(practice_button_frame, text="Restart", width=12, font=("Calibri", 14))
    restart_button.pack(side="left", padx=20)
    analytics_button = Button(practice_button_frame, text="View Analytics", width=12, font=("Calibri", 14))
    analytics_button.pack(side="left", padx=20)





