#!/usr/bin/env python3
import os, json
from terminalmon import terminalmon
import utils

JSON_DIR = "../json"
BUDDY_FILE = os.path.join(JSON_DIR, "buddy.json")

def main():
    print("🐚 Welcome to TerminalMon!\n")

    if not os.path.exists(JSON_DIR):
        os.makedirs(JSON_DIR)

    if not os.path.exists(BUDDY_FILE) or os.stat(BUDDY_FILE).st_size == 0:
        print("🎉 No TerminalMon found. Let's create your first one!\n")
        name = input("Enter your TerminalMon's name: ")

        # Create and set as buddy
        utils.create_terminalmon(name)
        utils.set_buddy(name)

        print(f"✅ {name} has been created and set as your buddy!\n")

    else:
        print("📦 Loading your buddy TerminalMon...\n")

    # Load the buddy and show stats
    tmon_data = utils.load_terminalmon()
    tmon = terminalmon(**tmon_data)
    tmon.print_stats()
    
    print("\n\n💡 TerminalMon loaded. Type tmon help for a list of commands and tmon quit to exit.\n\n")
    

if __name__ == "__main__":
    main()
