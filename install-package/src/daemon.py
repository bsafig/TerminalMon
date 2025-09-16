# daemon.py
import os
import socket
import json
import time
import utils
from terminalmon import terminalmon

SOCKET_PATH = "/tmp/tmon.sock"

def start_daemon():
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    print("🚀 TerminalMon daemon starting...")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET_PATH)
    sock.listen(1)

    try:
        tmon_data = utils.load_terminalmon()
        buddy_name = utils.get_buddy_name()
    except FileNotFoundError:
        print("No buddy found. Create one using: tmon new <name>")
        return

    tmon = terminalmon(**tmon_data)

    while True:
        conn, _ = sock.accept()
        try:
            data = conn.recv(1024).decode()
            if data:
                response, buddy_name = handle_command(tmon, data.strip(), buddy_name)
                conn.sendall(response.encode())
                if data.strip() == "quit":
                    break
        finally:
            conn.close()

    utils.save_terminalmon(tmon.get_stats(), name=buddy_name)
    print("🛑 TerminalMon daemon stopped.")
    sock.close()
    os.remove(SOCKET_PATH)

def handle_command(tmon, command, buddy_name):
    command = command.lower()

    if command == "stats":
        return tmon.print_stats() or "", buddy_name

    elif command.startswith("learn "):
        _, attack = command.split(" ", 1)
        tmon.learn_attack(attack)
        utils.save_terminalmon(tmon.get_stats(), name=buddy_name)
        return f"Learned attack: {attack}", buddy_name

    elif command.startswith("forget "):
        _, attack = command.split(" ", 1)
        tmon.forget_attack(attack)
        utils.save_terminalmon(tmon.get_stats(), name=buddy_name)
        return f"Forgot attack: {attack}", buddy_name

    elif command.startswith("new "):
        _, name = command.split(" ", 1)
        utils.create_terminalmon(name)
        return f"Created new TerminalMon: {name}", buddy_name

    elif command.startswith("buddy "):
        _, name = command.split(" ", 1)
        try:
            utils.set_buddy(name)
            tmon_data = utils.load_terminalmon()
            tmon.__init__(**tmon_data)
            return f"Set buddy to: {utils.colorize_name(name)}", name
        except FileNotFoundError:
            return f"TerminalMon {name} does not exist.", buddy_name

    elif command == "list":
        mons = utils.list_terminalmon()
        return "Created TerminalMon:\n" + "\n".join(mons), buddy_name

    elif command.startswith("xp "):
        try:
            _, amount = command.split(" ", 1)
            amount = int(amount)
            tmon.gain_xp(amount)
            utils.save_terminalmon(tmon.get_stats(), name=buddy_name)
            return f"Gained {amount} XP!", buddy_name
        except ValueError:
            return "Invalid XP amount.", buddy_name

    elif command.startswith("release "):
        _, name = command.split(" ", 1)
        if name == buddy_name:
            return "Cannot release your buddy TerminalMon.", buddy_name
        mons = utils.list_terminalmon()
        if name in mons:
            os.remove(os.path.join(utils.JSON_DIR, f"{name}.json"))
            return f"Released TerminalMon: {utils.colorize_name(name)}", buddy_name
        else:
            return f"TerminalMon {name} does not exist.", buddy_name

    elif command.startswith("editm "):
        try:
            _, old_name, new_name = command.split(" ", 2)
            old_path = os.path.join(utils.JSON_DIR, f"{old_name}.json")
            new_path = os.path.join(utils.JSON_DIR, f"{new_name}.json")
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                if buddy_name == old_name:
                    tmon.name = new_name
                    buddy_name = new_name
                    utils.set_buddy(new_name)
                    utils.save_terminalmon(tmon.get_stats(), name=new_name)
                return f"Renamed {utils.colorize_name(old_name)} to {utils.colorize_name(new_name)}", buddy_name
            else:
                return f"{old_name} does not exist.", buddy_name
        except Exception as e:
            return str(e), buddy_name

    elif command == "help":
        return (
            "Commands:\n"
            "stats - prints stats of buddy\n"
            "learn <move> - teaches a move\n"
            "forget <move> - forgets a move\n"
            "new <name> - creates a new TerminalMon\n"
            "buddy <name> - switch current buddy\n"
            "release <name> - deletes a TerminalMon\n"
            "editm <old> <new> - rename a TerminalMon\n"
            "xp <amount> - adds XP\n"
            "list - list all TerminalMon\n"
            "quit - stop daemon"
        , buddy_name)

    elif command == "quit":
        utils.save_terminalmon(tmon.get_stats(), name=buddy_name)
        return "Daemon quitting...", buddy_name

    else:
        return "Unknown command. Try: tmon help", buddy_name

if __name__ == "__main__":
    start_daemon()