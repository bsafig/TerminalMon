import json, utils

class terminalmon:
    def __init__(self, name, xp=0, level=1, learned_attacks=None, evolution_stage=0):
        self.name = name
        self.xp = xp
        self.level = level
        self.learned_attacks = learned_attacks or []
        self.evolution_stage = evolution_stage

    def gain_xp(self, amount):
        self.xp += amount
        self.check_level_up()

    def check_level_up(self):
        level_threshold = self.level * 10
        if self.xp >= level_threshold:
            self.xp -= level_threshold
            self.level += 1
            print(f"🎉 {self.name} leveled up to level {self.level}!")
            self.check_level_up()
            self.check_evolve()

    def check_evolve(self):
        if self.level in (30, 60, 90):
            self.evolution_stage += 1
            print(f"🔄 {self.name} has evolved to stage {self.evolution_stage}!")

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
            "learned_attacks": self.learned_attacks,
            "evolution_stage": self.evolution_stage
        }

    def print_stats(self):       
        print("TerminalMon Stats:")
        print(f"Name: {utils.colorize_name(self.name)}")
        print(f"Level: {self.level}")
        print(f"XP: {self.xp}/{self.level * 10}")
        print(f"Evolution Stage: {self.evolution_stage}")
        print(f"Learned Attacks: {', '.join(self.learned_attacks) or 'None'}")