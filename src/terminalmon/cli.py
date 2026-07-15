"""Command-line interface for TerminalMon.

Stateless: each invocation loads the buddy from disk, applies the command, and
saves. (There is no daemon, so no `start`/`quit` — every command is immediate
and persistent.)
"""
import argparse
import sys

from terminalmon import __version__, hook, storage
from terminalmon.model import TerminalMon


def _load_buddy():
    """Return the active buddy as a TerminalMon, printing a hint if none."""
    data = storage.load_buddy()
    if data is None:
        print("No buddy found. Create one with: tmon new <name>")
        return None
    return TerminalMon(**data)


# --- command handlers (each returns an exit code) ---------------------------

def cmd_stats(args):
    mon = _load_buddy()
    if not mon:
        return 1
    print(mon.format_stats())
    return 0


def cmd_xp(args):
    mon = _load_buddy()
    if not mon:
        return 1
    messages = mon.gain_xp(args.amount)
    storage.save_mon(mon.get_stats())
    print("\n".join(messages + [f"Gained {args.amount} XP!"]))
    return 0


def cmd_learn(args):
    mon = _load_buddy()
    if not mon:
        return 1
    if args.move in mon.moves:
        print(f"{mon.name} already knows {args.move}.")
        return 0
    mon.learn_move(args.move)
    storage.save_mon(mon.get_stats())
    print(f"{mon.name} learned {args.move}!")
    return 0


def cmd_forget(args):
    mon = _load_buddy()
    if not mon:
        return 1
    if args.move not in mon.moves:
        print(f"{mon.name} hasn't learned {args.move}.")
        return 1
    mon.forget_move(args.move)
    storage.save_mon(mon.get_stats())
    print(f"{mon.name} forgot {args.move}.")
    return 0


def cmd_use(args):
    mon = _load_buddy()
    if not mon:
        return 1
    if args.move not in mon.moves:
        print(f"{args.move} is not a learned move.")
        return 1
    if not storage.run_move(args.move):
        print(f"Move script {args.move}.sh not found.")
        return 1
    print(f"{mon.name} used {args.move}!")
    return 0


def cmd_edit(args):
    if args.path:
        storage.create_move(args.move)
        print(storage.move_path(args.move))
        return 0
    storage.edit_move(args.move)
    return 0


def cmd_new(args):
    if storage.mon_exists(args.name):
        print(f"TerminalMon {args.name} already exists.")
        return 1
    storage.create_mon(args.name)
    message = f"Created TerminalMon: {args.name}"
    if storage.get_buddy_name() is None:
        storage.set_buddy(args.name)
        message += " (set as your buddy)"
    print(message)
    return 0


def cmd_buddy(args):
    if not storage.mon_exists(args.name):
        print(f"TerminalMon {args.name} does not exist.")
        return 1
    storage.set_buddy(args.name)
    stage = storage.load_mon(args.name).get("evolution_stage", 0)
    print(f"Set buddy to: {storage.colorize_name(args.name, stage)}")
    return 0


def cmd_list(args):
    mons = storage.list_mons()
    if not mons:
        print("No TerminalMon yet. Create one with: tmon new <name>")
        return 0
    buddy = storage.get_buddy_name()
    lines = []
    for name in mons:
        stage = storage.load_mon(name).get("evolution_stage", 0)
        marker = " (buddy)" if name == buddy else ""
        lines.append(f"  {storage.colorize_name(name, stage)}{marker}")
    print("TerminalMon:\n" + "\n".join(lines))
    return 0


def cmd_rename(args):
    if not storage.mon_exists(args.old):
        print(f"{args.old} does not exist.")
        return 1
    if storage.mon_exists(args.new):
        print(f"{args.new} already exists.")
        return 1
    storage.rename_mon(args.old, args.new)
    print(f"Renamed {args.old} to {args.new}.")
    return 0


def cmd_release(args):
    if args.name == storage.get_buddy_name():
        print("Cannot release your buddy. Switch buddy first with: tmon buddy <name>")
        return 1
    if not storage.mon_exists(args.name):
        print(f"{args.name} does not exist.")
        return 1
    storage.release_mon(args.name)
    print(f"Released {args.name}.")
    return 0


def cmd_hook(args):
    print(hook.run(args.action, args.shell))
    return 0


def cmd_default(args):
    """`tmon` with no subcommand: first-run wizard, or show the buddy."""
    data = storage.load_buddy()
    if data is None:
        return first_run()
    print("📦 Loading your buddy TerminalMon...\n")
    print(TerminalMon(**data).format_stats())
    print("\n💡 Type `tmon --help` for the full command list.")
    return 0


def first_run():
    print("🐚 Welcome to TerminalMon!\n")
    print("🎉 No TerminalMon found. Let's create your first one!\n")
    name = input("Name your first TerminalMon: ").strip()
    if not name:
        print("No name given — run tmon again when you're ready.")
        return 1
    storage.create_mon(name)
    storage.set_buddy(name)
    print(f"\n✅ {name} created and set as your buddy!\n")
    print(TerminalMon(**storage.load_mon(name)).format_stats())
    return 0


# --- parser -----------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="tmon",
        description="Pokémon-inspired terminal companion that levels up as you use your shell.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.set_defaults(func=cmd_default)

    sub = parser.add_subparsers(dest="command", metavar="<command>")

    sub.add_parser("stats", help="show your buddy's stats").set_defaults(func=cmd_stats)

    p = sub.add_parser("xp", help="add XP to your buddy")
    p.add_argument("amount", type=int)
    p.set_defaults(func=cmd_xp)

    p = sub.add_parser("learn", help="learn a move")
    p.add_argument("move")
    p.set_defaults(func=cmd_learn)

    p = sub.add_parser("forget", help="forget a move")
    p.add_argument("move")
    p.set_defaults(func=cmd_forget)

    p = sub.add_parser("use", help="use a learned move")
    p.add_argument("move")
    p.set_defaults(func=cmd_use)

    p = sub.add_parser("edit", help="edit a move's script in your $EDITOR")
    p.add_argument("move")
    p.add_argument("--path", action="store_true", help="print the script path instead of opening an editor")
    p.set_defaults(func=cmd_edit)

    p = sub.add_parser("new", help="create a new TerminalMon")
    p.add_argument("name")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("buddy", help="switch your active buddy")
    p.add_argument("name")
    p.set_defaults(func=cmd_buddy)

    sub.add_parser("list", help="list all TerminalMon").set_defaults(func=cmd_list)

    p = sub.add_parser("rename", help="rename a TerminalMon")
    p.add_argument("old")
    p.add_argument("new")
    p.set_defaults(func=cmd_rename)

    p = sub.add_parser("release", help="delete a TerminalMon")
    p.add_argument("name")
    p.set_defaults(func=cmd_release)

    p = sub.add_parser("hook", help="manage the shell XP tracker")
    p.add_argument("action", choices=["install", "print"])
    p.add_argument("--shell", choices=["bash", "zsh"], help="target shell (default: autodetect)")
    p.set_defaults(func=cmd_hook)

    return parser


def main(argv=None):
    # Ensure emoji/ANSI output works regardless of the console's default codec.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main())
