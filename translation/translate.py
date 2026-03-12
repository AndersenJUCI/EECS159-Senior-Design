import json
import os
import threading
import keyboard

translation_state = {"active": False}

LEFT_KEYS = ["S", "T", "K", "P", "W", "H", "R"]
VOWELS = ["A", "O", "*", "E", "U"]
RIGHT_KEYS = ["F", "R", "P", "B", "L", "G", "T", "S", "D", "Z"]

RIGHT_DUPLICATE_MAPPING = {
    "R": "1",
    "P": "2",
    "T": "3",
    "S": "4",
    "F": "F",
    "B": "B",
    "L": "L",
    "G": "G",
    "D": "D",
    "Z": "Z"
}

STENO_ORDER = LEFT_KEYS + VOWELS + list(RIGHT_DUPLICATE_MAPPING.values())

STENO_DICT = {}
current_stroke = []
stroke_buffer = []
pressed_steno_keys = set()

REVERSE_RIGHT_MAPPING = {v: k for k, v in RIGHT_DUPLICATE_MAPPING.items()}

pending_timer = None
pending_outline = None
COMMIT_DELAY = 0.12


def load_active(dictionary_name):
    global STENO_DICT

    dictionaries = {}

    general_path = os.path.join("Dictionaries", "GeneralUse.json")
    if os.path.exists(general_path):
        with open(general_path, "r", encoding="utf-8") as file:
            dictionaries.update(json.load(file))

    if dictionary_name and dictionary_name not in ["GeneralUse", "None"]:
        selected_path = os.path.join("Dictionaries", f"{dictionary_name}.json")
        if os.path.exists(selected_path):
            with open(selected_path, "r", encoding="utf-8") as file:
                dictionaries.update(json.load(file))

    STENO_DICT = dictionaries


def build_chord():
    ordered_stroke = [key for key in STENO_ORDER if key in current_stroke]
    chord = ""
    for key in ordered_stroke:
        chord += REVERSE_RIGHT_MAPPING.get(key, key)
    return chord


def cancel_pending_commit():
    global pending_timer, pending_outline
    if pending_timer is not None:
        pending_timer.cancel()
        pending_timer = None
    pending_outline = None


def commit_pending_outline():
    global pending_timer, pending_outline, stroke_buffer

    outline_to_commit = pending_outline
    pending_timer = None
    pending_outline = None

    if outline_to_commit and outline_to_commit in STENO_DICT:
        keyboard.write(STENO_DICT[outline_to_commit] + " ")

    stroke_buffer.clear()


def start_pending_commit(outline):
    global pending_timer, pending_outline
    cancel_pending_commit()
    pending_outline = outline
    pending_timer = threading.Timer(COMMIT_DELAY, commit_pending_outline)
    pending_timer.daemon = True
    pending_timer.start()


def finish_stroke():
    global stroke_buffer, current_stroke

    chord = build_chord()
    current_stroke.clear()

    if not chord:
        return

    stroke_buffer.append(chord)
    full_outline = "/".join(stroke_buffer)

    exact_match = full_outline in STENO_DICT
    longer_matches = [k for k in STENO_DICT if k.startswith(full_outline + "/")]

    if exact_match and not longer_matches:
        cancel_pending_commit()
        keyboard.write(STENO_DICT[full_outline] + " ")
        stroke_buffer.clear()

    elif exact_match and longer_matches:
        start_pending_commit(full_outline)

    elif not exact_match and longer_matches:
        cancel_pending_commit()

    else:
        cancel_pending_commit()
        keyboard.write(f"[{full_outline}] ")
        stroke_buffer.clear()


def on_press(event):
    if not translation_state["active"]:
        return True

    key_name = event.name.upper()

    if key_name in STENO_ORDER:
        if not pressed_steno_keys:
            cancel_pending_commit()

        if key_name not in current_stroke:
            current_stroke.append(key_name)

        pressed_steno_keys.add(key_name)
        return False

    return True


def on_release(event):
    if not translation_state["active"]:
        return True

    key_name = event.name.upper()

    if key_name in STENO_ORDER:
        pressed_steno_keys.discard(key_name)

        if not pressed_steno_keys and current_stroke:
            finish_stroke()

        return False

    return True


def start_listener():
    listener_thread = threading.Thread(
        target=lambda: (
            keyboard.on_press(on_press, suppress=True),
            keyboard.on_release(on_release, suppress=True),
            keyboard.wait()
        ),
        daemon=True
    )
    listener_thread.start()


def reset_strokes():
    global current_stroke, stroke_buffer, pressed_steno_keys
    cancel_pending_commit()
    current_stroke.clear()
    stroke_buffer.clear()
    pressed_steno_keys.clear()