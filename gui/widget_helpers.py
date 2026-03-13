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
    return {"active_profile": None, "profiles": {}}


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

    Label(load_window, text="Select Profile:", font=("Calibri", 12)).pack(pady=(20, 5))
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

    Label(dialog, text="Select Profile", font=("Calibri", 12)).pack(pady=(20, 5))
    profile_var = StringVar()
    profile_var.set(list(profiles_data["profiles"].keys())[0])
    profile_dropdown = ttk.Combobox(
        dialog,
        textvariable=profile_var,
        values=list(profiles_data["profiles"].keys()),
        state="readonly"
    )
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

    Label(
        settings_window,
        text=f"Profile: {profiles_data['active_profile']}",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 14, "bold")
    ).pack(pady=(30, 10))
    Label(
        settings_window,
        text="Theme:",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 14, "bold")
    ).pack(pady=(10, 5))

    theme_var = StringVar()
    theme_var.set(profiles_data["profiles"][active_profile].get("theme", "Default"))

    theme_dropdown = ttk.Combobox(settings_window, textvariable=theme_var, state="readonly")
    theme_dropdown["values"] = list(themes.THEMES.keys())
    theme_dropdown.pack(pady=5)

    Label(
        settings_window,
        text="Dictionary:",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 14, "bold")
    ).pack(pady=(10, 5))
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

    add_word_button = Button(
        settings_window,
        text="Add Word",
        command=add_word,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 12)
    )
    add_word_button.pack(pady=(20, 10))

    save_button = Button(
        settings_window,
        text="Save Settings",
        command=save_settings,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 12)
    )
    save_button.pack(pady=20)


def show_help():
    global current_theme
    help_window = Toplevel(root)
    help_window.title("Help")
    window_width = 640
    window_height = 480
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

    summary_border = Frame(help_window, bg=current_theme["border_color"], bd=0)
    summary_border.pack(fill="both", expand=True, padx=10, pady=(15, 10))

    summary_text = Text(
        summary_border,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 11),
        wrap="word",
        height=10,
        bd=0,
        highlightthickness=0
    )
    summary_text.pack(fill="both", expand=True, padx=2, pady=2)

    summary_text.insert(
        "1.0",
        "What is stenography?\n"
        "Stenography is a method of typing where multiple keys are pressed at the same time "
        "to form a chord. Instead of entering words one letter at a time, a chord can represent "
        "a sound, a syllable, or even an entire word.\n\n"
        "How do I use it?\n"
        "To type in stenography, press the keys for a chord simultaneously and release them together. "
        "Some words are written in a single chord, while others require multiple chords.\n\n"
        "Translation symbols:\n"
        "/  separates multiple chords in one word.\n"
        "-  usually marks a right-hand sound or ending in an outline.\n"
        "*  is the asterisk key, which can modify or distinguish certain outlines.\n\n"
        "Example:\n"
        "PWOR/TKOPL means the word is written using two chords: PWOR and TKOPL.\n"
        "POP/KWRU/HRAR/TEU means the word uses four chords.\n\n"
        "In general, shorter and more common words often use fewer chords, while longer or more "
        "specialized words may require more."
    )

    summary_text.config(state="disabled")


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

    Label(
        lookup,
        text="Type the word you'd like the translation for",
        font=("Calibri", 14),
        bg=current_theme["bg"],
        fg=current_theme["fg"]
    ).pack(pady=(20, 10))

    word_var = StringVar()

    entry = Entry(lookup, textvariable=word_var, font=("Calibri", 14), width=25)
    entry.pack(pady=10)
    entry.focus_set()

    result_label = Label(
        lookup,
        text="Translation: ",
        font=("Calibri", 14, "bold"),
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        wraplength=420,
        justify="left"
    )
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
    window_width = 1080
    window_height = 720
    practice_window.geometry(f"{window_width}x{window_height}")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    practice_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    practice_window.resizable(False, False)
    practice_window.configure(bg=current_theme["bg"])
    practice_window.attributes("-toolwindow", True)

    def load_practice_dictionary():
        general_path = os.path.join(ROOT_DIR, "Dictionaries", "GeneralUse.json")
        if os.path.exists(general_path):
            try:
                with open(general_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        active_profile = profiles_data.get("active_profile")
        if active_profile:
            dictionary_name = profiles_data["profiles"][active_profile].get("dictionary")
            if dictionary_name and dictionary_name != "None":
                dictionary_path = os.path.join(ROOT_DIR, "Dictionaries", f"{dictionary_name}.json")
                if os.path.exists(dictionary_path):
                    try:
                        with open(dictionary_path, "r", encoding="utf-8") as f:
                            return json.load(f)
                    except Exception:
                        pass

        return {}

    def is_practice_word_valid(word):
        if not isinstance(word, str):
            return False
        word = word.strip()
        if not word:
            return False

        blocked_chars = "{}&^0123456789"
        if any(char in word for char in blocked_chars):
            return False

        lower_word = word.lower()
        allowed_chars = set("abcdefghijklmnopqrstuvwxyz'- ")
        if any(char not in allowed_chars for char in lower_word):
            return False

        if lower_word in {"a", "i"}:
            return True

        alpha_count = sum(1 for char in lower_word if char.isalpha())
        return alpha_count >= 2

    def is_outline_valid(outline):
        if not isinstance(outline, str):
            return False
        outline = outline.strip().upper()
        if not outline:
            return False

        blocked_chars = set("#*")
        if any(char in blocked_chars for char in outline):
            return False

        allowed_chars = set("STKPWHRAOEUFRPBLGTSDZ-/1234")
        return all(char in allowed_chars for char in outline)

    def build_lessons_from_dictionary(dictionary_data):
        valid_entries = []
        for outline, word in dictionary_data.items():
            if not is_outline_valid(outline):
                continue
            if not is_practice_word_valid(word):
                continue

            clean_word = word.strip().lower()
            strokes = outline.count("/") + 1
            word_length = len(clean_word.replace(" ", "").replace("'", "").replace("-", ""))

            valid_entries.append({
                "outline": outline,
                "word": clean_word,
                "strokes": strokes,
                "word_length": word_length
            })

        valid_entries.sort(key=lambda entry: (entry["strokes"], entry["word_length"], entry["word"], entry["outline"]))

        used_pairs = set()

        def select_entries(predicate, count):
            results = []
            for entry in valid_entries:
                pair = (entry["outline"], entry["word"])
                if pair in used_pairs:
                    continue
                if predicate(entry):
                    results.append(pair)
                    used_pairs.add(pair)
                    if len(results) == count:
                        break
            return results

        lessons_local = [
            {
                "title": "Lesson 1: Short Single-Stroke Words",
                "prompts": select_entries(
                    lambda entry: entry["strokes"] == 1 and entry["word_length"] <= 3 and " " not in entry["word"],
                    4
                )
            },
            {
                "title": "Lesson 2: Medium Single-Stroke Words",
                "prompts": select_entries(
                    lambda entry: entry["strokes"] == 1 and 4 <= entry["word_length"] <= 5 and " " not in entry["word"],
                    4
                )
            },
            {
                "title": "Lesson 3: Longer Single-Stroke Words",
                "prompts": select_entries(
                    lambda entry: entry["strokes"] == 1 and entry["word_length"] >= 6 and " " not in entry["word"],
                    4
                )
            },
            {
                "title": "Lesson 4: Short Two-Stroke Words",
                "prompts": select_entries(
                    lambda entry: entry["strokes"] == 2 and entry["word_length"] <= 6 and " " not in entry["word"],
                    4
                )
            },
            {
                "title": "Lesson 5: Longer Two-Stroke Words",
                "prompts": select_entries(
                    lambda entry: entry["strokes"] == 2 and entry["word_length"] >= 7 and " " not in entry["word"],
                    4
                )
            },
            {
                "title": "Lesson 6: Three-Stroke Words",
                "prompts": select_entries(
                    lambda entry: entry["strokes"] == 3 and " " not in entry["word"],
                    4
                )
            },
            {
                "title": "Lesson 7: Four+ Stroke Words",
                "prompts": select_entries(
                    lambda entry: entry["strokes"] >= 4 and " " not in entry["word"],
                    4
                )
            },
            {
                "title": "Lesson 8: Multi-Stroke Phrases",
                "prompts": select_entries(
                    lambda entry: entry["strokes"] >= 2 and " " in entry["word"],
                    4
                )
            },
            {
                "title": "Lesson 9: Advanced Long Words",
                "prompts": select_entries(
                    lambda entry: entry["word_length"] >= 10 and entry["strokes"] >= 2,
                    4
                )
            },
            {
                "title": "Lesson 10: Mixed Review",
                "prompts": []
            }
        ]

        mixed_review = []
        for lesson in lessons_local[:-1]:
            for prompt in lesson["prompts"]:
                if len(mixed_review) < 4:
                    mixed_review.append(prompt)

        if len(mixed_review) < 4:
            filler = select_entries(lambda entry: True, 4 - len(mixed_review))
            mixed_review.extend(filler)

        lessons_local[-1]["prompts"] = mixed_review[:4]

        fallback_prompts = select_entries(lambda entry: True, 20)

        for lesson in lessons_local:
            while len(lesson["prompts"]) < 4 and fallback_prompts:
                lesson["prompts"].append(fallback_prompts.pop(0))

        return lessons_local

    dictionary_data = load_practice_dictionary()
    lessons = build_lessons_from_dictionary(dictionary_data)

    analytics = {
        "attempted": 0,
        "correct": 0,
        "incorrect": 0
    }

    current_lesson_index = None
    current_prompt_index = 0

    list_frame = Frame(practice_window, bg=current_theme["bg"], width=220)
    list_frame.pack(side="left", fill="y", padx=10, pady=10)

    Label(
        list_frame,
        text="Tutorials",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 14, "bold")
    ).pack(pady=(0, 2))

    list_border = Frame(list_frame, bg=current_theme["border_color"], bd=0)
    list_border.pack(fill="both", expand=True, padx=4, pady=4)

    tutorial_list = Listbox(
        list_border,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0,
        highlightthickness=0,
        width=32,
        font=("Calibri", 12)
    )
    for lesson in lessons:
        tutorial_list.insert(END, lesson["title"])
    tutorial_list.pack(fill="y", expand=True, padx=2, pady=2)

    content_frame = Frame(practice_window, bg=current_theme["bg"])
    content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    instruction_label = Label(
        content_frame,
        text="Lesson: Select a lesson to begin.",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        wraplength=850,
        justify="left",
        font=("Calibri", 14, "bold")
    )
    instruction_label.pack(anchor="nw", pady=(0, 15))

    progress_label = Label(
        content_frame,
        text="Progress:",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        wraplength=850,
        justify="left",
        font=("Calibri", 12, "bold")
    )
    progress_label.pack(anchor="nw", pady=(0, 10))

    held_keys_label = Label(
        content_frame,
        text="Current Held Keys: None",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        wraplength=850,
        justify="left",
        font=("Calibri", 12, "bold")
    )
    held_keys_label.pack(anchor="nw", pady=(0, 10))

    visualizer_container = Frame(content_frame, bg=current_theme["bg"])
    visualizer_container.pack(anchor="nw", pady=(0, 15))

    Label(
        visualizer_container,
        text="Steno Visualizer (Translation must be ON):",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 12, "bold")
    ).pack(anchor="w", pady=(0, 8))

    visualizer_frame = Frame(visualizer_container, bg=current_theme["bg"])
    visualizer_frame.pack(anchor="w")

    steno_key_widgets = {}

    def create_visualizer_key(parent, token, text):
        key_label = Label(
            parent,
            text=text,
            width=4,
            height=2,
            bg=current_theme["bg"],
            fg=current_theme["fg"],
            relief="solid",
            bd=1,
            font=("Calibri", 11, "bold")
        )
        key_label.pack(side="left", padx=2, pady=2)
        steno_key_widgets[token] = key_label

    top_row = Frame(visualizer_frame, bg=current_theme["bg"])
    top_row.pack(anchor="w")
    for token, text in [
        ("L_S", "S"), ("L_T", "T"), ("L_K", "K"), ("L_P", "P"),
        ("L_W", "W"), ("L_H", "H"), ("L_R", "R")
    ]:
        create_visualizer_key(top_row, token, text)

    vowel_row = Frame(visualizer_frame, bg=current_theme["bg"])
    vowel_row.pack(anchor="w")
    for token, text in [
        ("V_A", "A"), ("V_O", "O"), ("V_*", "*"), ("V_E", "E"), ("V_U", "U")
    ]:
        create_visualizer_key(vowel_row, token, text)

    bottom_row = Frame(visualizer_frame, bg=current_theme["bg"])
    bottom_row.pack(anchor="w")
    for token, text in [
        ("R_F", "F"), ("R_R", "R"), ("R_P", "P"), ("R_B", "B"), ("R_L", "L"),
        ("R_G", "G"), ("R_T", "T"), ("R_S", "S"), ("R_D", "D"), ("R_Z", "Z")
    ]:
        create_visualizer_key(bottom_row, token, text)

    answer_frame = Frame(content_frame, bg=current_theme["bg"])
    answer_frame.pack(anchor="nw", pady=(0, 15))

    Label(
        answer_frame,
        text="Enter typed word:",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 12, "bold")
    ).pack(side="left", padx=(0, 10))

    answer_var = StringVar()
    answer_entry = Entry(answer_frame, textvariable=answer_var, font=("Calibri", 12), width=25)
    answer_entry.pack(side="left")

    result_label = Label(
        content_frame,
        text="Result:",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        wraplength=850,
        justify="left",
        font=("Calibri", 12, "bold")
    )
    result_label.pack(anchor="nw", pady=(0, 15))

    text_border = Frame(content_frame, bg=current_theme["border_color"], bd=0)
    text_border.pack(fill="x", padx=4, pady=4)

    text_box = Text(
        text_border,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        height=8,
        font=("Calibri", 12),
        bd=0,
        highlightthickness=0
    )
    text_box.pack(fill="x", padx=2, pady=2)

    practice_button_frame = Frame(content_frame, bg=current_theme["bg"], bd=0)
    practice_button_frame.pack(side="bottom", fill="x", pady=10)

    def display_prompt():
        if current_lesson_index is None:
            return

        lesson = lessons[current_lesson_index]
        chord, word = lesson["prompts"][current_prompt_index]

        instruction_label.config(
            text=f"Lesson: {lesson['title']}\n\nType this word: '{word}'"
        )
        progress_label.config(
            text=f"Progress: Prompt {current_prompt_index + 1} of {len(lesson['prompts'])}"
        )
        result_label.config(text="Result:", fg=current_theme["fg"])
        answer_var.set("")
        answer_entry.focus_set()

        text_box.delete("1.0", END)
        text_box.insert(END, f"Target word: {word}\n")
        text_box.insert(END, f"Expected chord: {chord}\n")
        text_box.insert(END, "Use the visualizer to watch your held steno keys in real time.\n")
        text_box.insert(END, "Note: the visualizer updates from the translation engine, so Translation should be ON.\n")

    def select_lesson():
        nonlocal current_lesson_index, current_prompt_index
        selected_lesson = tutorial_list.curselection()
        if not selected_lesson:
            return
        current_lesson_index = selected_lesson[0]
        current_prompt_index = 0
        display_prompt()

    def check_answer():
        if current_lesson_index is None:
            messagebox.showwarning("No Lesson Selected", "Please select a lesson first.", parent=practice_window)
            return

        lesson = lessons[current_lesson_index]
        chord, expected_word = lesson["prompts"][current_prompt_index]
        user_answer = answer_var.get().strip().lower()

        if not user_answer:
            result_label.config(text="Result: Please enter a word.", fg="orange")
            return

        analytics["attempted"] += 1

        if user_answer == expected_word.lower():
            analytics["correct"] += 1
            result_label.config(text=f"Result: Correct! Expected chord: {chord}", fg="lime")
        else:
            analytics["incorrect"] += 1
            result_label.config(
                text=f"Result: Incorrect. Expected word: '{expected_word}' | Chord: {chord}",
                fg="red"
            )

    def next_prompt():
        nonlocal current_prompt_index
        if current_lesson_index is None:
            return

        lesson = lessons[current_lesson_index]

        if current_prompt_index < len(lesson["prompts"]) - 1:
            current_prompt_index += 1
            display_prompt()
        else:
            instruction_label.config(text=f"Lesson: {lesson['title']}\n\nLesson complete.")
            progress_label.config(text="Progress: Complete")
            text_box.delete("1.0", END)
            text_box.insert(END, "You completed this lesson.\n")
            result_label.config(text="Result:", fg=current_theme["fg"])

    def restart_lesson():
        nonlocal current_prompt_index
        if current_lesson_index is None:
            return
        current_prompt_index = 0
        display_prompt()

    def show_analytics_window():
        analytics_window = Toplevel(practice_window)
        analytics_window.title("Practice Analytics")
        analytics_window.geometry("400x250")
        analytics_window.resizable(False, False)
        analytics_window.configure(bg=current_theme["bg"])
        analytics_window.grab_set()

        attempted = analytics["attempted"]
        correct = analytics["correct"]
        incorrect = analytics["incorrect"]
        accuracy = (correct / attempted * 100) if attempted > 0 else 0

        Label(
            analytics_window,
            text="Practice Analytics",
            bg=current_theme["bg"],
            fg=current_theme["fg"],
            font=("Calibri", 16, "bold")
        ).pack(pady=(20, 20))

        Label(
            analytics_window,
            text=f"Words Attempted: {attempted}",
            bg=current_theme["bg"],
            fg=current_theme["fg"],
            font=("Calibri", 12)
        ).pack(pady=5)

        Label(
            analytics_window,
            text=f"Correct: {correct}",
            bg=current_theme["bg"],
            fg=current_theme["fg"],
            font=("Calibri", 12)
        ).pack(pady=5)

        Label(
            analytics_window,
            text=f"Incorrect: {incorrect}",
            bg=current_theme["bg"],
            fg=current_theme["fg"],
            font=("Calibri", 12)
        ).pack(pady=5)

        Label(
            analytics_window,
            text=f"Accuracy: {accuracy:.2f}%",
            bg=current_theme["bg"],
            fg=current_theme["fg"],
            font=("Calibri", 12, "bold")
        ).pack(pady=5)

    def get_active_visualizer_tokens():
        pressed = getattr(trans, "pressed_steno_keys", set())
        active_tokens = set()

        for raw_key in pressed:
            key = str(raw_key).upper()

            if key == "S":
                active_tokens.add("L_S")
            elif key == "T":
                active_tokens.add("L_T")
            elif key == "K":
                active_tokens.add("L_K")
            elif key == "P":
                active_tokens.add("L_P")
            elif key == "W":
                active_tokens.add("L_W")
            elif key == "H":
                active_tokens.add("L_H")
            elif key == "R":
                active_tokens.add("L_R")
            elif key == "A":
                active_tokens.add("V_A")
            elif key == "O":
                active_tokens.add("V_O")
            elif key == "*":
                active_tokens.add("V_*")
            elif key == "E":
                active_tokens.add("V_E")
            elif key == "U":
                active_tokens.add("V_U")
            elif key == "F":
                active_tokens.add("R_F")
            elif key in {"1", "F1"}:
                active_tokens.add("R_R")
            elif key in {"2", "F2"}:
                active_tokens.add("R_P")
            elif key == "B":
                active_tokens.add("R_B")
            elif key == "L":
                active_tokens.add("R_L")
            elif key == "G":
                active_tokens.add("R_G")
            elif key in {"3", "F3"}:
                active_tokens.add("R_T")
            elif key in {"4", "F4"}:
                active_tokens.add("R_S")
            elif key == "D":
                active_tokens.add("R_D")
            elif key == "Z":
                active_tokens.add("R_Z")

        return active_tokens

    def get_held_keys_text():
        pressed = getattr(trans, "pressed_steno_keys", set())
        if not pressed:
            return "Current Held Keys: None"

        internal_order = [
            "S", "T", "K", "P", "W", "H", "R",
            "A", "O", "*", "E", "U",
            "F", "1", "2", "B", "L", "G", "3", "4", "D", "Z"
        ]

        normalized = set()
        for raw_key in pressed:
            key = str(raw_key).upper()
            if key in {"F1"}:
                normalized.add("1")
            elif key in {"F2"}:
                normalized.add("2")
            elif key in {"F3"}:
                normalized.add("3")
            elif key in {"F4"}:
                normalized.add("4")
            else:
                normalized.add(key)

        display_parts = []
        for key in internal_order:
            if key in normalized:
                if key == "1":
                    display_parts.append("R")
                elif key == "2":
                    display_parts.append("P")
                elif key == "3":
                    display_parts.append("T")
                elif key == "4":
                    display_parts.append("S")
                else:
                    display_parts.append(key)

        return "Current Held Keys: " + "".join(display_parts)

    def refresh_visualizer():
        if not practice_window.winfo_exists():
            return

        active_tokens = get_active_visualizer_tokens()
        for token, widget in steno_key_widgets.items():
            if token in active_tokens:
                widget.config(bg=current_theme["border_color"], fg="white")
            else:
                widget.config(bg=current_theme["bg"], fg=current_theme["fg"])

        held_keys_label.config(text=get_held_keys_text())
        practice_window.after(50, refresh_visualizer)

    begin_button = Button(
        practice_button_frame,
        text="Select Lesson",
        command=select_lesson,
        width=12,
        font=("Calibri", 14)
    )
    begin_button.pack(side="left", padx=10)

    check_button = Button(
        practice_button_frame,
        text="Check Answer",
        command=check_answer,
        width=12,
        font=("Calibri", 14)
    )
    check_button.pack(side="left", padx=10)

    next_button = Button(
        practice_button_frame,
        text="Next Prompt",
        command=next_prompt,
        width=12,
        font=("Calibri", 14)
    )
    next_button.pack(side="left", padx=10)

    restart_button = Button(
        practice_button_frame,
        text="Restart Lesson",
        command=restart_lesson,
        width=12,
        font=("Calibri", 14)
    )
    restart_button.pack(side="left", padx=10)

    analytics_button = Button(
        practice_button_frame,
        text="View Analytics",
        command=show_analytics_window,
        width=12,
        font=("Calibri", 14)
    )
    analytics_button.pack(side="left", padx=10)

    answer_entry.bind("<Return>", lambda event: check_answer())
    refresh_visualizer()