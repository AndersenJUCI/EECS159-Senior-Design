"""
Theme Structure And Methods

Functions:
- get_theme(name) -> dict
- apply_theme(widget, theme, border_frame=None)
"""

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

def get_theme(name: str):
    return THEMES.get(name, THEMES["Default"])

def apply_theme(widget, theme: dict, border_frame=None):
    if widget is None or theme is None:
        return
    try:
        if widget == border_frame:
            widget.configure(bg=theme["border_color"])
        else:
            widget.configure(bg=theme["bg"])
    except Exception:
        pass

    try:
        widget.configure(fg=theme["fg"])
    except Exception:
        pass

    for child in widget.winfo_children():
        apply_theme(child, theme, border_frame=border_frame)
