"""Shell XP-tracking hook: install or print the snippet for the user's shell.

The hook feeds XP to TerminalMon based on the length of each command you run.
"""
import os
from importlib.resources import files
from pathlib import Path

MARKER = "# TerminalMon XP Hook"

RC_FILES = {
    "bash": "~/.bashrc",
    "zsh": "~/.zshrc",
}


def detect_shell():
    """Best-effort shell name from $SHELL, defaulting to bash."""
    name = os.path.basename(os.environ.get("SHELL", "bash"))
    return "zsh" if "zsh" in name else "bash"


def snippet(shell):
    return files("terminalmon.shell").joinpath(f"hook.{shell}").read_text()


def install(shell):
    rc = Path(RC_FILES[shell]).expanduser()
    existing = rc.read_text(encoding="utf-8") if rc.exists() else ""
    if MARKER in existing:
        return f"⚠️  TerminalMon XP tracker already present in {rc}."
    with open(rc, "a", encoding="utf-8") as f:
        f.write("\n" + snippet(shell) + "\n")
    return (
        f"✅ TerminalMon XP tracker added to {rc}.\n"
        f"Restart your shell or run: source {rc}"
    )


def run(action, shell=None):
    shell = shell or detect_shell()
    if shell not in RC_FILES:
        return f"Unsupported shell: {shell}. Choose bash or zsh."
    if action == "print":
        return snippet(shell)
    if action == "install":
        return install(shell)
    return "Usage: tmon hook {install,print} [--shell bash|zsh]"
