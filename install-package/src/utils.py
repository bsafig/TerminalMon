import os
import json
import shutil

JSON_DIR = "../json"
BUDDY_FILE = os.path.join(JSON_DIR, "buddy.json")

def load_terminalmon():
    with open(BUDDY_FILE, 'r') as file:
        return json.load(file)

def save_terminalmon(data):
    with open(BUDDY_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def set_buddy(name):
    source_file = os.path.join(JSON_DIR, f"{name}.json")
    shutil.copyfile(source_file, BUDDY_FILE)

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
    mons = []
    for file in os.listdir(JSON_DIR):
        if file.endswith(".json") and file != "buddy.json":
            mons.append(file[:-5])  # Remove .json extension
    return mons

def colorize_name(name):
    evolution_stage = load_terminalmon().get("evolution_stage", 0)
    colors = {
        1: "\033[97m",  # White
        2: "\033[94m",  # Blue
        3: "\033[91m",  # Red
        4: "\033[95m",  # Purple
    }
    reset = "\033[0m"
    try:
        color = colors[evolution_stage]
    except IndexError:
        color = "\033[97m"  # fallback to white
    return f"{color}{name}{reset}"
