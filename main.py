import pyxel
import random

WIDTH, HEIGHT = 128, 128

STATE_REAL = 0
STATE_SPIRIT = 1

class Game:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Connexion")
        self.state = STATE_REAL
        self.player = {"x": 64, "y": 64, "vx": 0, "vy": 0, "hp": 5, "faith": 100}
        self.portals = [{"x": 32, "y": 32, "purified": False},
                        {"x": 96, "y": 96, "purified": False}]
        self.spirit_nodes = []
        self.monsters = []
        self.ritual_active = False
        self.ritual_progress = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        self.update_player()
        if self.state == STATE_REAL:
            self.update_real()
        else:
            self.update_spirit()

    def update_player(self):
        self.player["vx"] = (pyxel.btn(pyxel.KEY_RIGHT) - pyxel.btn(pyxel.KEY_LEFT)) * 1.5
        self.player["vy"] = (pyxel.btn(pyxel.KEY_DOWN) - pyxel.btn(pyxel.KEY_UP)) * 1.5
        self.player["x"] = max(0, min(WIDTH-1, self.player["x"] + self.player["vx"]))
        self.player["y"] = max(0, min(HEIGHT-1, self.player["y"] + self.player["vy"]))

    def update_real(self):
        for p in self.portals:
            if not p["purified"] and self.dist(self.player, p) < 6:
                if pyxel.btnp(pyxel.KEY_SPACE):
                    self.start_ritual()

        if self.ritual_active:
            self.ritual_progress += 1
            if self.ritual_progress % 10 == 0:
                self.player["faith"] = max(0, self.player["faith"] - 1)
            if self.ritual_progress >= 60:
                self.enter_spirit()

    def update_spirit(self):
        if pyxel.frame_count % 30 == 0:
            self.player["faith"] = max(0, self.player["faith"] - 2)
            if self.player["faith"] == 0:
                self.exit_spirit(failed=True)

        for m in self.monsters:
            dx = 1 if self.player["x"] > m["x"] else -1
            dy = 1 if self.player["y"] > m["y"] else -1
            m["x"] += dx * m["spd"]
            m["y"] += dy * m["spd"]
            if self.dist(self.player, m) < 5:
                self.player["hp"] = max(0, self.player["hp"] - 1)

        all_purified = all(n["purified"] for n in self.spirit_nodes) if self.spirit_nodes else False
        if all_purified:
            self.exit_spirit(failed=False)

        if pyxel.btnp(pyxel.KEY_Z):
            for m in self.monsters:
                if self.dist(self.player, m) < 8:
                    m["hp"] -= 1
            self.monsters = [m for m in self.monsters if m["hp"] > 0]

    def start_ritual(self):
        self.ritual_active = True
        self.ritual_progress = 0

    def enter_spirit(self):
        self.state = STATE_SPIRIT
        self.ritual_active = False
        self.spirit_nodes = [{"x": 30, "y": 30, "purified": False},
                             {"x": 96, "y": 40, "purified": False}]
        self.monsters = [{"x": 10, "y": 10, "hp": 2, "spd": 0.5},
                         {"x": 110, "y": 100, "hp": 3, "spd": 0.7}]

    def exit_spirit(self, failed):
        self.state = STATE_REAL
        if not failed:
            for p in self.portals:
                if not p["purified"]:
                    p["purified"] = True
                    break
        self.spirit_nodes.clear()
        self.monsters.clear()

    def draw(self):
        pyxel.cls(0)
        if self.state == STATE_REAL:
            self.draw_real()
        else:
            self.draw_spirit()
        self.draw_ui()  

    def draw_real(self):
        for p in self.portals:
            col = 11 if p["purified"] else 2
            pyxel.circ(p["x"], p["y"], 3, col)
        pyxel.rect(0, 0, WIDTH, HEIGHT, 1)
        pyxel.circ(self.player["x"], self.player["y"], 3, 7)
        if self.ritual_active:
            pyxel.text(5, 5, "Rituel...", 10)

    def draw_spirit(self):
        pyxel.rect(0, 0, WIDTH, HEIGHT, 5)
        for n in self.spirit_nodes:
            col = 10 if n["purified"] else 8
            pyxel.circ(n["x"], n["y"], 3, col)
        for m in self.monsters:
            pyxel.circ(m["x"], m["y"], 3, 3)
        pyxel.circ(self.player["x"], self.player["y"], 3, 14)

    def draw_ui(self):
        pyxel.text(5, HEIGHT-15, f"HP: {self.player['hp']}", 7)
        pyxel.text(50, HEIGHT-15, f"Faith: {self.player['faith']}", 7)

    @staticmethod
    def dist(a, b):
        return ((a["x"] - b["x"])**2 + (a["y"] - b["y"])**2) ** 0.5

Game()

