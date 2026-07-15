"""Persistence for TerminalMon.

Each creature is a single JSON file under ``mons/``. The active buddy is just
a name recorded in the ``buddy`` pointer file — there is no separate cached
copy to keep in sync. Move scripts live under ``moves/``.
"""
import json
import os
import subprocess
import sys

from terminalmon import paths


# --- low-level JSON helpers -------------------------------------------------

def _read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, data):
    paths.ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# --- creatures --------------------------------------------------------------

def mon_path(name):
    return paths.mons_dir() / f"{name}.json"


def mon_exists(name):
    return mon_path(name).exists()


def new_mon_data(name):
    return {
        "name": name,
        "xp": 0,
        "level": 1,
        "moves": [],
        "evolution_stage": 0,
    }


def create_mon(name):
    _write_json(mon_path(name), new_mon_data(name))


def load_mon(name):
    return _read_json(mon_path(name))


def save_mon(data):
    _write_json(mon_path(data["name"]), data)


def list_mons():
    directory = paths.mons_dir()
    if not directory.exists():
        return []
    return sorted(p.stem for p in directory.glob("*.json"))


def release_mon(name):
    mon_path(name).unlink()


def rename_mon(old, new):
    data = load_mon(old)
    data["name"] = new
    _write_json(mon_path(new), data)
    mon_path(old).unlink()
    if get_buddy_name() == old:
        set_buddy(new)


# --- buddy pointer ----------------------------------------------------------

def get_buddy_name():
    try:
        return paths.buddy_pointer().read_text(encoding="utf-8").strip() or None
    except FileNotFoundError:
        return None


def set_buddy(name):
    paths.ensure_dirs()
    paths.buddy_pointer().write_text(name, encoding="utf-8")


def load_buddy():
    """Return the active buddy's data dict, or None if there isn't one."""
    name = get_buddy_name()
    if not name or not mon_exists(name):
        return None
    return load_mon(name)


# --- move scripts -----------------------------------------------------------

def move_path(name):
    return paths.moves_dir() / f"{name}.sh"


def create_move(name):
    path = move_path(name)
    if not path.exists():
        paths.ensure_dirs()
        path.write_text(
            f"#!/bin/bash\n# {name} move script\n\necho '🌀 {name} used!'\n",
            encoding="utf-8",
            newline="\n",
        )
        os.chmod(path, 0o755)


def run_move(name):
    path = move_path(name)
    if not path.exists():
        return False
    # Honour the script's own shebang so users can swap interpreters; if the
    # file isn't directly executable (e.g. exec bit lost), fall back to bash.
    try:
        subprocess.run([str(path)], check=False)
    except OSError:
        subprocess.run(["bash", str(path)], check=False)
    return True


def edit_move(name):
    create_move(name)
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"
    subprocess.run([editor, str(move_path(name))], check=False)


def delete_move(name):
    path = move_path(name)
    if path.exists():
        path.unlink()


def move_used_elsewhere(name, exclude_mon):
    for mon in list_mons():
        if mon == exclude_mon:
            continue
        if name in load_mon(mon).get("moves", []):
            return True
    return False


# --- presentation -----------------------------------------------------------

_COLORS = {
    0: "\033[97m",  # White
    1: "\033[92m",  # Green
    2: "\033[93m",  # Yellow
    3: "\033[94m",  # Blue
    4: "\033[91m",  # Red
    5: "\033[96m",  # Cyan
    6: "\033[95m",  # Purple
}
_RESET = "\033[0m"


def _use_color():
    return (
        sys.stdout.isatty()
        and os.environ.get("NO_COLOR") is None
        and os.environ.get("TERM") != "dumb"
    )


def colorize_name(name, stage=0):
    if not _use_color():
        return name
    return f"{_COLORS.get(stage, _COLORS[0])}{name}{_RESET}"
