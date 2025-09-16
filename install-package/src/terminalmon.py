import json

class terminalmon:
    def __init__(self, name, xp=0, level=1, learned_attacks=None):
        self.name = name
        self.xp = xp
        self.level = level
        self.learned_attacks = learned_attacks or []
        self.can_evolve = False

    def gain_xp(self, amount):
        self.xp += amount
        self.check_level_up()

    def check_level_up(self):
        level_threshold = pow(10, self.level)
        if self.xp >= level_threshold:
            self.xp -= level_threshold
            self.level += 1
            print(f"🎉 {self.name} leveled up to level {self.level}!")
            self.check_level_up()
            self.check_evolve()

    def check_evolve(self):
        if self.level in (30, 60, 90):
            self.can_evolve = True
            print(f"🔥 {self.name} can now evolve!")

    def evolve(self, new_name):
        if self.can_evolve:
            oldname = self.name
            self.name = new_name
            self.can_evolve = False
            print(f"🌟 {oldname} evolved into {self.name}!")

    def learn_attack(self, attack_name):
        if attack_name not in self.learned_attacks:
            self.learned_attacks.append(attack_name)
    
    def forget_attack(self, attack_name):
        if attack_name in self.learned_attacks:
            self.learned_attacks.remove(attack_name)

    def get_stats(self):
        return {
            "name": self.name,
            "xp": self.xp,
            "level": self.level,
            "learned_attacks": self.learned_attacks
        }

    def print_stats(self):
        print("📊 TerminalMon Stats:")
        print(json.dumps(self.get_stats(), indent=4))
