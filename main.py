import pyxel
import math
import random

WIDTH, HEIGHT = 256, 256

STATE_REAL = 0
STATE_SPIRIT = 1

class Game:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Broken Places", fps= 30, quit_key= pyxel.KEY_RCTRL, display_scale= 4)
        pyxel.load("5.pyxres")
        pyxel.mouse(True)

        # Player
        self.player = {
            "x": 800,
            "y": 1200,
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
            {"x": 32, "y": 32, "purified": False, "type": "portal"},
            {"x": 96, "y": 96, "purified": False, "type": "portal"},
            {"x": 410, "y": 1304, "purified": False, "type": "headlight"},
            {"x": 1086, "y": 1444, "purified": False, "type": "headlight"},
            {"x": 1464, "y": 1082, "purified": False, "type": "headlight"}
        ]
        
        self.tile_type= {
            "no_collision_terrain": None,
            "terrain": [1],
            "entrance": [0, 1],
            "sign": [4, 3],
            "forest": [0, 3],
            "path": None,
            "water": [0, 1, 5, 12],
            "wood_bridge": [0],
            "brick_bridge": [0, 1],
            "graveyard": [1, 13]
        }
        self.tile_id_collision= {
            'no_collision_terrain': [(0, 0), (19, 0), (20, 0), (19, 1), (20, 1), (17, 2), (19, 2), (20, 2), (17, 3), (18, 3), (19, 3), (20, 3), (17, 4), (18, 4), (19, 4), (20, 4), (21, 4), (17, 5), (18, 5), (19, 5), (20, 5), (21, 5), (17, 6), (18, 6), (19, 6), (20, 6), (21, 6), (5, 11), (13, 11), (15, 11), (16, 11), (0, 12), (3, 12), (5, 13), (6, 13), (8, 13), (14, 13), (14, 14), (0, 15), (3, 15), (15, 15), (16, 15), (30, 30)],
            'terrain': [(1, 0), (2, 0), (3, 0), (4, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (0, 5), (4, 5), (5, 5), (6, 5), (4, 6), (5, 6), (6, 6), (22, 6), (23, 6), (17, 7), (18, 7), (19, 7), (20, 7), (21, 7), (22, 7), (23, 7), (17, 8), (18, 8), (19, 8), (20, 8), (21, 8), (22, 8), (23, 8), (17, 9), (18, 9), (19, 9), (20, 9), (17, 10), (18, 10), (19, 10), (20, 10), (1, 15), (2, 15), (13, 15), (14, 15)],
            'entrance': [(3, 5), (3, 6), (3, 7), (3, 8)],
            'sign': [(7, 4), (2, 5), (7, 5)],
            'forest': [(22, 4), (23, 4), (24, 4), (25, 4), (22, 5), (23, 5), (24, 5), (25, 5), (24, 6), (25, 6), (24, 7), (25, 7), (24, 8), (25, 8), (22, 9), (23, 9), (24, 9), (25, 9), (22, 10), (23, 10), (31,30)],
            'path': [(8, 4), (11, 4), (8, 5), (11, 5), (0, 6), (1, 6), (2, 6), (7, 6), (8, 6), (0, 7), (1, 7), (2, 7), (6, 7), (0, 8), (1, 8), (2, 8), (3, 9), (5, 9), (6, 9), (7, 9), (8, 9), (1, 12), (2, 12), (4, 12), (5, 12), (6, 12), (7, 12), (0, 13), (1, 13), (2, 13), (3, 13), (4, 13), (7, 13), (0, 14), (1, 14), (2, 14), (3, 14), (4, 14), (7, 14)],
            'water': [(9, 0), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0), (17, 0), (18, 0), (9, 1), (10, 1), (11, 1), (12, 1), (13, 1), (14, 1), (15, 1), (16, 1), (17, 1), (18, 1), (9, 2), (10, 2), (15, 2), (16, 2), (18, 2), (9, 3), (10, 3), (15, 3), (16, 3), (15, 4), (16, 4), (1, 5), (15, 5), (16, 5), (15, 6), (16, 6), (4, 7), (5, 7), (15, 7), (16, 7), (4, 8), (5, 8), (9, 8), (10, 8), (11, 8), (12, 8), (13, 8), (14, 8), (15, 8), (16, 8), (0, 9), (1, 9), (2, 9), (9, 9), (10, 9), (11, 9), (12, 9), (13, 9), (14, 9), (15, 9), (16, 9), (0, 10), (1, 10), (2, 10), (3, 10), (4, 10), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10), (0, 11), (1, 11), (2, 11), (3, 11), (4, 11), (6, 11), (7, 11), (8, 11), (9, 11), (10, 11), (11, 11), (8, 12), (9, 12), (10, 12), (11, 12), (5, 14), (6, 14), (4, 15), (5, 15), (6, 15), (7, 15), (30, 29), (30, 27)],
            'wood_bridge': [(6, 8), (4, 9), (9, 13), (10, 13), (11, 13), (12, 13), (12, 14), (12, 15)],
            'brick_bridge': [(9, 4), (10, 4), (9, 5), (10, 5), (12, 5), (13, 5), (14, 5), (12, 6), (13, 6), (14, 6), (12, 7), (13, 7), (14, 7), (7, 7), (8, 7), (7, 8), (8, 8)],
            'graveyard': [(12, 10), (13, 10), (14, 10), (15, 10), (16, 10), (12, 11), (14, 11), (12, 12), (13, 12), (14, 12), (15, 12), (16, 12), (13, 13), (15, 13), (13, 14), (15, 14)]
            }
        self.tree_id= {"1": 0, "2": 16, "3": 32, "4": 48, "5": 64, "6": 80}
        self.cactus_id= {"1": 96}
        self.rock_id= {"1": 64, "2": 72, "3": 80, "4": 88}
        self.bush_id= {"1": 64, "2": 72, "3": 80, "4": 88}
        self.trees= []
        self.cactus= []
        self.bushs= []
        self.rocks= []
        for i in range(184, 1736):
            self.trees+= [[]]
            self.rocks+= [[]]
            self.bushs+= [[]]
        
        for i in range(1312, 1656):
            self.cactus+= [[]]
        
        for tile_y in range(240):
            for tile_x in range(200):
                
                if pyxel.tilemaps[0].pget(tile_x, tile_y)==(31,30):
                    for i in range(1):
                        self.trees[tile_y*8+random.randint(1,7)-184]+= [[tile_x*8+random.randint(1,7), str(random.randint(1,6))]]
                
                elif pyxel.tilemaps[0].pget(tile_x, tile_y)==(30,27):
                    for i in range(random.choice([0,1])):
                        self.trees[tile_y*8+random.randint(1,7)-184]+= [[tile_x*8+random.randint(1,7), str(random.randint(1,6))]]
                        
                elif pyxel.tilemaps[0].pget(tile_x, tile_y)==(0,0):
                    for i in range(random.choice([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1])):
                        tmp= random.randint(1, 3)
                        if tmp==1:
                            self.trees[tile_y*8+random.randint(1,7)-184]+= [[tile_x*8+random.randint(1,7), str(random.randint(1,6))]]
                        elif tmp==2:
                            self.bushs[tile_y*8+random.randint(1,7)-184]+= [[tile_x*8+random.randint(1,7), str(random.randint(1,4))]]
                        else:
                            self.rocks[tile_y*8+random.randint(1,7)-184]+= [[tile_x*8+random.randint(1,7), str(random.randint(1,4))]]
                        
                        
                elif pyxel.tilemaps[0].pget(tile_x, tile_y)==(30,30):
                    for i in range(random.choice([0,0,0,0,0,0,0,0,0,0,1])):
                        self.cactus[tile_y*8+random.randint(1,7)-1312]+= [[tile_x*8+random.randint(1,7), str(random.randint(1,1))]]
        
        

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
        
        tile_of_player= pyxel.tilemaps[0].pget((self.player["x"]+move[0]* 2)//8+16, (self.player["y"]+move[1]* 2)//8+16)
        
        #print(tile_of_player, ((self.player["x"]+move[0] * 2)%8, (self.player["y"]+move[1] * 2)%8),pyxel.image(0).pget(tile_of_player[0]*8+self.player["x"]%8+move[0] * 1, tile_of_player[1]*8+self.player["y"]%8+move[1] * 1))

        for type_of_tile in self.tile_type:
            if self.tile_id_collision[type_of_tile].count(tile_of_player)==1:
                if self.tile_type[type_of_tile]!=None:
                    if self.tile_type[type_of_tile].count(pyxel.image(0).pget(tile_of_player[0]*8+(self.player["x"]+move[0] * 2)%8+move[0] * 1, tile_of_player[1]*8+(self.player["y"]+move[1] * 2)%8+move[1] * 1))==1:
                        move= (0,0)
                        
        
        self.player["vx"] = move[0] * 5
        self.player["vy"] = move[1] * 5
        #                                      v : taille de la map
        self.player["x"] = max(-WIDTH//2, min(1596, self.player["x"] + self.player["vx"]))
        self.player["y"] = max(-HEIGHT//2, min(1916, self.player["y"] + self.player["vy"]))
        
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
    
    def draw_tree(self):
        for y in range(len(self.trees)):
            for tree in self.trees[y]:
                pyxel.blt(tree[0]-self.player["x"]-8, y+184-self.player["y"]-8, 0, 240, self.tree_id[tree[1]], 16, 16, 7)
                
    def draw_cactus(self):
        for y in range(len(self.cactus)):
            for cactus in self.cactus[y]:
                pyxel.blt(cactus[0]-self.player["x"]-8, y+1312-self.player["y"]-8, 0, 240, self.cactus_id[cactus[1]], 16, 16, 7)
                
    def draw_bush(self):
        for y in range(len(self.bushs)):
            for bush in self.bushs[y]:
                pyxel.blt(bush[0]-self.player["x"]-8, y+184-self.player["y"]-8, 0, self.bush_id[bush[1]], 112, 8, 8, 7)
    
    def draw_rock(self):
        for y in range(len(self.rocks)):
            for rock in self.rocks[y]:
                pyxel.blt(rock[0]-self.player["x"]-8, y+184-self.player["y"]-8, 0, self.rock_id[rock[1]], 120, 8, 8, 7)
    
        
            
    # -------------------------------

    def draw_real(self):
        pyxel.cls(1)
        
        pyxel.bltm(0, 0, 0, self.player["x"], self.player["y"], WIDTH, HEIGHT)

        self.draw_tree()
        self.draw_cactus()
        self.draw_bush()
        self.draw_rock()
        
        pyxel.blt(WIDTH//2-4, HEIGHT//2-4, 0, 40, 0, 8, 8, 7)
        
        # Aura animée autour des portails
        for p in self.portals:
            if not p["purified"]:
                if p["type"]=="portal":
                    r = 6 + (pyxel.frame_count % 8)
                    pyxel.circ(p["x"]-self.player["x"]+WIDTH//2, p["y"]-self.player["y"]+HEIGHT//2, r, 13)
                if p["type"]=="headlight":
                    pass

        # Portails
        for p in self.portals:
            if p["type"]=="portal":
                col = 11 if p["purified"] else 2
                pyxel.circ(p["x"]-self.player["x"]+WIDTH//2, p["y"]-self.player["y"]+HEIGHT//2, 3, col)
            if p["type"]=="headlight":
                    pyxel.blt(p["x"]-self.player["x"]+WIDTH//2, p["y"]-self.player["y"]+HEIGHT//2, 2, 0, 0, 47, 111, 4)

        # Arbres
        

        # Joueur animé
        #col = 7 if self.player["anim"] == 0 else 10
        
        

        # Rituel visuel
        if self.ritual_active:
            pyxel.circb(WIDTH//2, HEIGHT//2,
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



