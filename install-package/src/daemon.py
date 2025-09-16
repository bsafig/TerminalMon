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

    # Load or create the buddy TerminalMon
    try:
        tmon_data = utils.load_terminalmon()
    except FileNotFoundError:
        print("No buddy found. Create one using: tmon create")
        return

    tmon = terminalmon(**tmon_data)

    while True:
        conn, _ = sock.accept()
        try:
            data = conn.recv(1024).decode()
            if data:
                response = handle_command(tmon, data.strip())
                conn.sendall(response.encode())
                if data.strip() == "quit":
                    break
        finally:
            conn.close()

    utils.save_terminalmon(tmon.get_stats())
    print("🛑 TerminalMon daemon stopped.")
    sock.close()
    os.remove(SOCKET_PATH)

def handle_command(tmon, command):
    command = command.lower()
    if command == "stats":
        return json.dumps(tmon.get_stats(), indent=4)
    elif command.startswith("learn "):
        _, attack = command.split(" ", 1)
        tmon.learn_attack(attack)
        utils.save_terminalmon(tmon.get_stats())
        return f"Learned attack: {attack}"
    elif command.startswith("forget "):
        try:
            _, attack = command.split(" ", 1)
            tmon.forget_attack(attack)
            utils.save_terminalmon(tmon.get_stats())
            return f"Forgot attack: {attack}"
        except:
            return f"Attack {attack} not known."
    elif command.startswith("new "):
        _, name = command.split(" ", 1)
        utils.create_terminalmon(name)
        return f"Created new TerminalMon: {name}"
    elif command.startswith("buddy "):
        try:
            _, name = command.split(" ", 1)
            utils.set_buddy(name)
            tmon_data = utils.load_terminalmon()
            tmon = terminalmon(**tmon_data)
            utils.save_terminalmon(tmon.get_stats())
            return f"Set buddy to: {name}"
        except FileNotFoundError:
            return f"TerminalMon {name} does not exist."
    elif command == "list":
        mons = utils.list_terminalmon()
        return "Created TerminalMon:\n" + "\n".join(mons)
    elif command.startswith("xp "):
        try:
            _, amount = command.split(" ", 1)
            amount = int(amount)
            tmon.gain_xp(amount)
            utils.save_terminalmon(tmon.get_stats())
            return f"Gained {amount} XP!"
        except ValueError:
            return "Invalid XP amount."
    elif command == "help":
        return "Commands:\nstats - prints stats of buddy TerminalMon\nlearn <move> - teaches script of name move to buddy TerminalMon\nforget <move> - forgets a learned move\nnew <name> - creates a new TerminalMon with name <name>\nbuddy <name> - changes the current buddy TerminalMon to an existing Mon with name <name>\nlist - displays a list of all created TerminalMon\nquit"
    elif command == "quit":
        utils.save_terminalmon(tmon.get_stats())
        return "Daemon quitting..."
    else:
        return "Unknown command. Try: stats, xp <amount>, learn <attack>, quit"

if __name__ == "__main__":
    start_daemon()
