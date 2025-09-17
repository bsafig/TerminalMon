# daemon.py
import os
import socket
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
    parts = command.split(" ", 1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd == "stats":
        return tmon.print_stats() or "", buddy_name

    elif cmd == "learn":
        tmon.learn_attack(arg)
        utils.save_terminalmon(tmon.get_stats(), name=buddy_name)
        return f"Learned attack: {arg}", buddy_name

    elif cmd == "forget":
        tmon.forget_attack(arg)
        utils.save_terminalmon(tmon.get_stats(), name=buddy_name)
        return f"Forgot attack: {arg}", buddy_name

    elif cmd == "edita":
        message = utils.edit_attack_script(arg)
        return message, buddy_name


    elif cmd == "use":
        if arg in tmon.learned_attacks:
            ran = utils.run_attack_script(arg)
            if ran:
                return f"Used {arg}!", buddy_name
            return f"Attack script {arg}.sh not found.", buddy_name
        return f"{arg} is not a learned attack.", buddy_name

    elif cmd == "new":
        utils.create_terminalmon(arg)
        return f"Created new TerminalMon: {arg}", buddy_name

    elif cmd == "buddy":
        try:
            utils.set_buddy(arg)
            tmon_data = utils.load_terminalmon()
            tmon.__init__(**tmon_data)
            return f"Set buddy to: {utils.colorize_name(arg)}", arg
        except FileNotFoundError:
            return f"TerminalMon {arg} does not exist.", buddy_name

    elif cmd == "list":
        return "Created TerminalMon:\n" + "\n".join(utils.list_terminalmon()), buddy_name

    elif cmd == "xp":
        try:
            amount = int(arg)
            tmon.gain_xp(amount)
            utils.save_terminalmon(tmon.get_stats(), name=buddy_name)
            return f"Gained {amount} XP!", buddy_name
        except ValueError:
            return "Invalid XP amount.", buddy_name

    elif cmd == "release":
        if arg == buddy_name:
            return "Cannot release your buddy TerminalMon.", buddy_name
        if arg in utils.list_terminalmon():
            os.remove(os.path.join(utils.JSON_DIR, f"{arg}.json"))
            return f"Released TerminalMon: {utils.colorize_name(arg)}", buddy_name
        return f"TerminalMon {arg} does not exist.", buddy_name

    elif cmd == "editm":
        try:
            old_name, new_name = arg.split(" ")
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

    elif cmd == "help":
        return (
            "Commands:\n"
            "stats - prints stats of buddy\n"
            "learn <move> - teaches a move\n"
            "forget <move> - forgets a move\n"
            "edita <move> - edit move script\n"
            "use <move> - run move script\n"
            "new <name> - creates a new TerminalMon\n"
            "buddy <name> - switch current buddy\n"
            "release <name> - deletes a TerminalMon\n"
            "editm <old> <new> - rename a TerminalMon\n"
            "xp <amount> - adds XP\n"
            "list - list all TerminalMon\n"
            "quit - stop daemon"
        , buddy_name)

    elif cmd == "quit":
        utils.save_terminalmon(tmon.get_stats(), name=buddy_name)
        return "Daemon quitting...", buddy_name

    return "Unknown command. Try: tmon help", buddy_name

if __name__ == "__main__":
    start_daemon()