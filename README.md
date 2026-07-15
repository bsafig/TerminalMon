# TerminalMon

Pokémon-inspired terminal experience. Gain XP by running shell commands and
earn and use "moves" (custom scripts). Unaffiliated with official Pokémon
branding — all names are original and user-created.

## Features

- Name a TerminalMon that gains XP as you use your shell.
- Level up (every `level × 10` XP) and evolve at levels 30, 60, and 90.
- Learn, forget, and run "moves" (shell scripts).
- Keep multiple TerminalMon, switch your buddy, rename, and release them.

## Install

TerminalMon is a Python package. It runs on Linux and macOS (Unix shells).

```bash
pip install terminalmon
```

or, to keep it isolated:

```bash
pipx install terminalmon
```

This puts the `tmon` command on your PATH.

### Enable XP tracking

To earn XP automatically from the commands you run, install the shell hook:

```bash
tmon hook install            # auto-detects bash or zsh from $SHELL
tmon hook install --shell zsh
```

Then restart your shell (or `source ~/.bashrc` / `source ~/.zshrc`).
Prefer to wire it up yourself? `tmon hook print` emits the snippet.

## Usage

Run `tmon` with no arguments the first time to create your buddy:

```bash
tmon
```

Every command runs immediately and saves to disk — there is no daemon to
start or stop. Run `tmon --help` (or `tmon <command> --help`) for details.

| Command | Description |
|---|---|
| `tmon stats` | Show your buddy's stats |
| `tmon xp <amount>` | Add XP |
| `tmon learn <move>` | Learn a move (creates its script) |
| `tmon forget <move>` | Forget a move |
| `tmon use <move>` | Run a learned move |
| `tmon edit <move>` | Open a move's script in your `$EDITOR` (`--path` prints the path instead) |
| `tmon new <name>` | Create a new TerminalMon |
| `tmon buddy <name>` | Switch your active buddy |
| `tmon list` | List all TerminalMon |
| `tmon rename <old> <new>` | Rename a TerminalMon |
| `tmon release <name>` | Delete a TerminalMon (not your buddy) |
| `tmon hook install` | Install the shell XP tracker |

## Where data is stored

TerminalMon stores your creatures and move scripts in your per-user data
directory (e.g. `~/.local/share/terminalmon` on Linux,
`~/Library/Application Support/terminalmon` on macOS). Set the
`TERMINALMON_HOME` environment variable to override the location.

Move scripts are opened with `$VISUAL`/`$EDITOR` (falling back to `vi`).
Colored output is disabled automatically when piped or when `NO_COLOR` is set.

## Development

```bash
git clone https://github.com/bsafig/TerminalMon
cd TerminalMon
pip install -e ".[dev]"
pytest
```
