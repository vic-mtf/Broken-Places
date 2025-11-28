import pyxel
import math
import random

WIDTH, HEIGHT = 256, 256

STATE_REAL = 0
STATE_SPIRIT = 1

class Game:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Broken Places", fps= 30, quit_key= pyxel.KEY_RCTRL, display_scale= 3)
        pyxel.load("5.pyxres")
        pyxel.mouse(True)

        # Player
        self.player = {
            "x": 64,
            "y": 64,
            "vx": 0,
            "vy": 0,
            "hp": 5,
            "faith": 100,
            "anim": 0,  # animation frame
            "immortality": False,
            "immortality_start_frame": 0
        }

        # World
        self.state = STATE_REAL
        self.portals = [
            {"x": 32, "y": 32, "purified": False},
            {"x": 96, "y": 96, "purified": False}
        ]

        # Spirit world
        self.spirit_nodes = []
        self.monsters = []
        self.projectiles = []
        self.particles = []       # pour effets d’impact visibles
        self.memory_fragments = []

        # Ritual
        self.ritual_active = False
        self.ritual_progress = 0

        pyxel.run(self.update, self.draw)

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self):
        self.update_player()

        if self.state == STATE_REAL:
            self.update_real()
        else:
            self.update_spirit()

    def update_player(self):
        move = ((pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT)) - (pyxel.btn(pyxel.KEY_Q) or pyxel.btn(pyxel.KEY_LEFT)),
                (pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN)) - (pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.KEY_UP)))

        self.player["vx"] = move[0] * 1.5
        self.player["vy"] = move[1] * 1.5

        self.player["x"] = max(0, min(WIDTH, self.player["x"] + self.player["vx"]))
        self.player["y"] = max(0, min(HEIGHT, self.player["y"] + self.player["vy"]))
        
        if self.player["immortality"]==True and pyxel.frame_count-self.player["immortality_start_frame"]>15:
            self.player["immortality"]= False

        # animation du joueur
        if move != (0, 0):
            if pyxel.frame_count % 10 == 0:
                self.player["anim"] = 1 - self.player["anim"]

    # ============================================================
    # REAL WORLD
    # ============================================================

    def update_real(self):
        near_portal = None

        for p in self.portals:
            if not p["purified"] and self.dist(self.player, p) < 10:
                near_portal = p

        # Rituel
        if near_portal:
            if pyxel.btn(pyxel.KEY_SPACE):
                self.ritual_active = True
                self.ritual_progress += 1

                if self.ritual_progress % 12 == 0:
                    self.player["faith"] -= 1

                if self.ritual_progress >= 60:
                    self.enter_spirit()
            else:
                # si SPACE relâché, reset
                if self.ritual_active:
                    self.ritual_active = False
                    self.ritual_progress = 0

    # ============================================================
    # SPIRIT WORLD
    # ============================================================

    def update_spirit(self):

        # Perte de foi progressive
        if pyxel.frame_count % 30 == 0:
            self.player["faith"] -= 2
            if self.player["faith"] <= 0:
                self.exit_spirit(failed=True)

        # -------------------------------
        # ATTAQUE À DISTANCE (LEFT CLICK)
        # -------------------------------
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            dif_x= (self.player["x"])-pyxel.mouse_x
            dif_y= (self.player["y"])-pyxel.mouse_y
            if dif_x==0:
                dx= 0
                dy= -dif_y/abs(dif_x)
            elif dif_y==0:
                dx= -dif_x/abs(dif_y)
                dy=0
            elif abs(dif_x) > abs(dif_y):
                dx= -dif_x/abs(dif_x)
                dy= -dif_y/abs(dif_x)
            else:
                dx= -dif_x/abs(dif_y)
                dy= -dif_y/abs(dif_y)

            # défaut : tir vers la droite
            if dx == 0 and dy == 0:
                dx = 1

            self.projectiles.append({
                "x": self.player["x"],
                "y": self.player["y"],
                "dx": dx,
                "dy": dy,
                "spd": 3,
                "life": 40
            })

        # -------------------------------
        # UPDATE PROJECTILES
        # -------------------------------
        for p in self.projectiles:
            p["x"] += p["dx"] * p["spd"]
            p["y"] += p["dy"] * p["spd"]
            p["life"] -= 1

        # -------------------------------
        # MONSTRES → mouvement + contact
        # -------------------------------
        for m in self.monsters:
            dx = 1 if self.player["x"] > m["x"] else -1
            dy = 1 if self.player["y"] > m["y"] else -1
            m["x"] += dx * m["spd"]
            m["y"] += dy * m["spd"]

            m["anim"] = (pyxel.frame_count // 10) % 2

            # contact joueur
            if self.dist(self.player, m) < 6:
                if self.player["immortality"]==False:
                    self.player["hp"] -= 1
                    self.player["immortality"]=True
                    self.player["immortality_start_frame"]= pyxel.frame_count

        # -------------------------------
        # COLLISIONS projectile → monstre
        # -------------------------------
        for p in self.projectiles:
            for m in self.monsters:
                if self.dist(p, m) < 6:
                    m["hp"] -= 1
                    p["life"] = 0
                    self.spawn_hit_particles(m["x"], m["y"])

        # nettoyer
        self.projectiles = [p for p in self.projectiles if p["life"] > 0]
        self.monsters = [m for m in self.monsters if m["hp"] > 0]

        # -------------------------------
        # PURIFICATION DES NŒUDS SPIRITUELS
        # -------------------------------
        for n in self.spirit_nodes:
            if not n["purified"] and self.dist(self.player, n) < 8:
                if pyxel.btnp(pyxel.KEY_SPACE):
                    n["purified"] = True
                    self.spawn_hit_particles(n["x"], n["y"])

        # tout purifié ?
        if self.spirit_nodes and all(n["purified"] for n in self.spirit_nodes):
            self.exit_spirit(failed=False)

        # update des particules
        for h in self.particles:
            h["x"] += h["dx"]
            h["y"] += h["dy"]
            h["life"] -= 1

        self.particles = [h for h in self.particles if h["life"] > 0]

    # ============================================================
    # PARTICULES VISUELLES
    # ============================================================

    def spawn_hit_particles(self, x, y):
        for _ in range(6):
            angle = random.random() * 6.28
            speed = random.uniform(0.5, 1.5)
            self.particles.append({
                "x": x,
                "y": y,
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "life": random.randint(10, 20)
            })

    # ============================================================
    # EVENTS
    # ============================================================

    def enter_spirit(self):
        self.state = STATE_SPIRIT
        self.ritual_active = False
        self.ritual_progress = 0
        self.player["immortality"]= True

        # Noeuds à purifier
        self.spirit_nodes = [
            {"x": 30, "y": 30, "purified": False},
            {"x": 96, "y": 40, "purified": False}
        ]

        # Monstres animés
        self.monsters = [
            {"x": 20, "y": 20, "hp": 3, "spd": 0.5, "anim": 0},
            {"x": 110, "y": 100, "hp": 4, "spd": 0.6, "anim": 0}
        ]

    def exit_spirit(self, failed):
        self.state = STATE_REAL

        if not failed:
            # purifier un portail
            for p in self.portals:
                if not p["purified"]:
                    p["purified"] = True
                    self.memory_fragments.append(
                        random.choice([
                            "« Une fracture traverse encore le monde... »",
                            "Une ombre murmure : « Tu te souviens ? »",
                            "Une larme tombe dans la poussière.",
                            "Un ancien cri déchire ton esprit.",
                        ])
                    )
                    break

        self.spirit_nodes.clear()
        self.monsters.clear()
        self.projectiles.clear()
        self.particles.clear()

    # ============================================================
    # DRAW
    # ============================================================

    def draw(self):
        if self.state == STATE_REAL:
            self.draw_real()
        else:
            self.draw_spirit()

        self.draw_ui()

    # -------------------------------

    def draw_real(self):
        pyxel.cls(1)

        # Aura animée autour des portails
        for p in self.portals:
            if not p["purified"]:
                r = 6 + (pyxel.frame_count % 8)
                pyxel.circ(p["x"], p["y"], r, 13)

        # Portails
        for p in self.portals:
            col = 11 if p["purified"] else 2
            pyxel.circ(p["x"], p["y"], 3, col)

        # Joueur animé
        col = 7 if self.player["anim"] == 0 else 10
        #pyxel.circ(self.player["x"], self.player["y"], 3, col)
        pyxel.blt(self.player["x"]-4, self.player["y"]-4, 0, 40, 0, 8, 8, 7)

        # Rituel visuel
        if self.ritual_active:
            pyxel.circb(self.player["x"], self.player["y"],
                        20 - self.ritual_progress // 3,
                        10)

    # -------------------------------

    def draw_spirit(self):
        # Fond pulsant
        c = 5 + (pyxel.frame_count % 20) // 5
        pyxel.cls(c)

        # Noeuds spirituels
        for n in self.spirit_nodes:
            col = 10 if n["purified"] else 8
            pyxel.circ(n["x"], n["y"], 3, col)

        # Monstres animés
        for m in self.monsters:
            col = 3 if m["anim"] == 0 else 6
            pyxel.circ(m["x"], m["y"], 3, col)

        # Projectiles
        for p in self.projectiles:
            pyxel.circ(p["x"], p["y"], 1, 7)

        # Particules
        for h in self.particles:
            pyxel.pset(h["x"], h["y"], 7)

        # Joueur
        col = 14 if self.player["anim"] == 0 else 7
        #pyxel.circ(self.player["x"], self.player["y"], 3, col)
        pyxel.blt(self.player["x"]-8, self.player["y"]-8, 1, 80, 0, 16, 16, 7)

    # -------------------------------

    def draw_ui(self):
        pyxel.text(5, HEIGHT - 15, f"HP:{self.player['hp']}", 7)
        pyxel.text(50, HEIGHT - 15, f"Faith:{self.player['faith']}", 7)

        if self.memory_fragments:
            pyxel.text(5, 5, self.memory_fragments[-1], 6)

    # -------------------------------

    @staticmethod
    def dist(a, b):
        return ((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2) ** 0.5


Game()


