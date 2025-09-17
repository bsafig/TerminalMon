# utils.py
import os
import json
import shutil

JSON_DIR = "../json"
BUDDY_FILE = os.path.join(JSON_DIR, "buddy.json")
BUDDY_NAME_TRACK = os.path.join(JSON_DIR, "buddy_name.txt")

def load_terminalmon():
    with open(BUDDY_FILE, 'r') as file:
        return json.load(file)

def save_terminalmon(data, name=None):
    with open(BUDDY_FILE, 'w') as file:
        json.dump(data, file, indent=4)

    if not name:
        name = get_buddy_name()

    if name:
        filepath = os.path.join(JSON_DIR, f"{name}.json")
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)

def set_buddy(name):
    filepath = os.path.join(JSON_DIR, f"{name}.json")
    shutil.copyfile(filepath, BUDDY_FILE)
    with open(BUDDY_NAME_TRACK, 'w') as f:
        f.write(name)

def get_buddy_name():
    try:
        with open(BUDDY_NAME_TRACK, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def create_terminalmon(name):
    file_path = os.path.join(JSON_DIR, f"{name}.json")
    data = {
        "name": name,
        "xp": 0,
        "level": 1,
        "learned_attacks": [],
        "evolution_stage": 0
    }
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def list_terminalmon():
    return [
        file[:-5] for file in os.listdir(JSON_DIR)
        if file.endswith(".json") and file != "buddy.json"
    ]

def colorize_name(name):
    evolution_stage = load_terminalmon().get("evolution_stage", 0)
    colors = {
        0: "\033[97m",  # White
        1: "\033[92m",  # Green
        2: "\033[93m",  # Yellow
        3: "\033[94m",  # Blue
        4: "\033[91m",  # Red
        5: "\033[96m",  # Cyan
        6: "\033[95m",  # Purple
    }
    reset = "\033[0m"
    try:
        color = colors[evolution_stage]
    except IndexError:
        color = "\033[97m"  # fallback to white
    return f"{color}{name}{reset}"