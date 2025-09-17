# utils.py
import os
import json
import shutil
import subprocess

JSON_DIR = "../json"
SCRIPT_DIR = "../scripts"
BUDDY_FILE = os.path.join(JSON_DIR, "buddy.json")
BUDDY_NAME_TRACK = os.path.join(JSON_DIR, "buddy_name.txt")

# Ensure directories exist
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(SCRIPT_DIR, exist_ok=True)

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
    return f"{colors.get(evolution_stage, '\033[97m')}{name}{reset}"

def create_attack_script(name):
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    path = os.path.join(SCRIPT_DIR, f"{name}.sh")
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(f"#!/bin/bash\n# {name} attack script\n\necho '🌀 {name} attack activated!'\n")
        os.chmod(path, 0o755)

def edit_attack_script(name):
    path = os.path.join(SCRIPT_DIR, f"{name}.sh")
    if not os.path.exists(path):
        create_attack_script(name)

    # Attach vim to current TTY to behave properly even from daemon context
    os.system(f"bash -c 'exec </dev/tty; vim {path}'")

def run_attack_script(name):
    path = os.path.join(SCRIPT_DIR, f"{name}.sh")
    if os.path.exists(path):
        os.system(path)
        return True
    return False

def is_attack_used_elsewhere(move_name, current_mon_name):
    for mon_file in os.listdir(JSON_DIR):
        if not mon_file.endswith(".json") or mon_file == "buddy.json":
            continue
        name = mon_file[:-5]
        if name == current_mon_name:
            continue
        path = os.path.join(JSON_DIR, mon_file)
        with open(path, 'r') as f:
            data = json.load(f)
            if move_name in data.get("learned_attacks", []):
                return True
    return False

def delete_attack_script(name):
    path = os.path.join(SCRIPT_DIR, f"{name}.sh")
    if os.path.exists(path):
        os.remove(path)