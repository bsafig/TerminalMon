"""Filesystem locations for TerminalMon user data.

Data lives in a per-user data directory (never inside the installed package),
overridable with the ``TERMINALMON_HOME`` environment variable. These are
functions rather than module constants so the override is honoured at call
time (which also keeps them testable).
"""
import os
from pathlib import Path

from platformdirs import user_data_dir


def base_dir() -> Path:
    override = os.environ.get("TERMINALMON_HOME")
    if override:
        return Path(override).expanduser()
    return Path(user_data_dir("terminalmon"))


def mons_dir() -> Path:
    return base_dir() / "mons"


def moves_dir() -> Path:
    return base_dir() / "moves"


def buddy_pointer() -> Path:
    """File holding the name of the currently active buddy."""
    return base_dir() / "buddy"


def ensure_dirs() -> None:
    mons_dir().mkdir(parents=True, exist_ok=True)
    moves_dir().mkdir(parents=True, exist_ok=True)
