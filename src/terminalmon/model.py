"""The TerminalMon creature model."""
from terminalmon import storage


class TerminalMon:
    def __init__(self, name, xp=0, level=1, moves=None, evolution_stage=0):
        self.name = name
        self.xp = xp
        self.level = level
        self.moves = moves or []
        self.evolution_stage = evolution_stage

    def gain_xp(self, amount):
        """Add XP and return a list of level-up / evolution messages."""
        self.xp += amount
        return self.check_level_up()

    def check_level_up(self):
        messages = []
        level_threshold = self.level * 10
        while self.xp >= level_threshold:
            self.xp -= level_threshold
            self.level += 1
            messages.append(
                f"🎉 {storage.colorize_name(self.name, self.evolution_stage)} "
                f"leveled up to level {self.level}!"
            )
            messages.extend(self.check_evolve())
            level_threshold = self.level * 10
        return messages

    def check_evolve(self):
        messages = []
        if (self.level % 30 == 0) and self.evolution_stage < 6:
            self.evolution_stage += 1
            messages.append(
                f"🔄 {storage.colorize_name(self.name, self.evolution_stage)} "
                f"evolved to stage {self.evolution_stage}!"
            )
        return messages

    def learn_move(self, move_name):
        if move_name not in self.moves:
            self.moves.append(move_name)
            storage.create_move(move_name)

    def forget_move(self, move_name):
        if move_name in self.moves:
            self.moves.remove(move_name)
            if not storage.move_used_elsewhere(move_name, self.name):
                storage.delete_move(move_name)

    def get_stats(self):
        return {
            "name": self.name,
            "xp": self.xp,
            "level": self.level,
            "moves": self.moves,
            "evolution_stage": self.evolution_stage,
        }

    def format_stats(self):
        name = storage.colorize_name(self.name, self.evolution_stage)
        moves = ", ".join(self.moves) or "None"
        return (
            "📊 TerminalMon Stats:\n"
            f"Name: {name}\n"
            f"Level: {self.level}\n"
            f"XP: {self.xp}/{self.level * 10}\n"
            f"Evolution Stage: {self.evolution_stage}\n"
            f"Moves: {moves}"
        )
