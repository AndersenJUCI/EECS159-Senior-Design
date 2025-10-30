from tkinter import *
from tkinter import ttk

import gui.widget_helpers as helpers

def main_bar(root, main_frame, system_tray, current_theme, border_frame):

    # ---------------- Top Frame ----------------
    top_bar = Frame(main_frame, bg=current_theme["bg"], height=50)
    top_bar.pack(side="top", fill="x")

    # ---------------- Title And Profile ----------------
    logo = Label(
        top_bar,
        text="⌨  Stenography Keyboard",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Arial", 20, "bold")
    )
    logo.pack(side="left", padx=(0, 30))

    separator = ttk.Separator(top_bar, orient="vertical")
    separator.pack(side="left", fill="y", padx=2)

    # ---------------- Profile Buttons ----------------

    profile_label = Label(
        top_bar,
        text="Profile:",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 16, "bold")
    )
    profile_label.pack(side="left", padx=(0, 2))

    new_profile_button = Button(
        top_bar,
        text="🆕 New",
        command=helpers.new_profile,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0,
        font=("Calibri", 16)
    )
    new_profile_button.pack(side="left", padx=2)

    load_profile_button = Button(
        top_bar,
        text="📂 Load",
        command=helpers.load_profile,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0,
        font=("Calibri", 16)
    )
    load_profile_button.pack(side="left", padx=2)

    edit_profile_button = Button(
        top_bar,
        text="🖊 Edit",
        command=helpers.edit_profile,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0,
        font=("Calibri", 16)
    )
    edit_profile_button.pack(side="left", padx=2)

    save_profile_button = Button(
        top_bar,
        text="💾 Save",
        command=helpers.save_current_profile,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0,
        font=("Calibri", 16)
    )
    save_profile_button.pack(side="left", padx=2)

    separator = ttk.Separator(top_bar, orient="vertical")
    separator.pack(side="left", fill="y", padx=2)

    # ---------------- Dictionary Buttons ----------------

    dictionary_label = Label(
        top_bar,
        text="Dictionary:",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        font=("Calibri", 16, "bold")
    )
    dictionary_label.pack(side="left", padx=(0, 2))

    import_dictionary_button = Button(
        top_bar,
        text="⬇ Import",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0,
        font=("Calibri", 16)
    )
    import_dictionary_button.pack(side="left", padx=2)

    export_dictionary_button = Button(
        top_bar,
        text="⬆ Export",
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0,
        font=("Calibri", 16)
    )
    export_dictionary_button.pack(side="left", padx=2)

    separator = ttk.Separator(top_bar, orient="vertical")
    separator.pack(side="left", fill="y", padx=2)

    # ---------------- Menu Buttons ----------------

    exit_button = Button(
        top_bar,
        text="❌",
        command=system_tray.quit_app,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0
    )
    exit_button.pack(side="right", padx=2)

    minimize_button = Button(
        top_bar,
        text="━",
        command=system_tray.minimize,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0
    )
    minimize_button.pack(side="right", padx=2)

    settings_button = Button(
        top_bar, text="⚙️",
        command=helpers.show_settings,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0
    )
    settings_button.pack(side="right", padx=2)

    help_button = Button(
        top_bar,
        text="❓",
        command=helpers.show_help,
        bg=current_theme["bg"],
        fg=current_theme["fg"],
        bd=0
    )
    help_button.pack(side="right", padx=2)

    return top_bar

