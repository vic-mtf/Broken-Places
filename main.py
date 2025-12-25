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

        self.hud= None
        self.settings= False
        self.pause_ui_text_id= [
            (107, 48, 29),
            (72, 48, 35),
            (72, 40, 63),
            (72, 40, 23),
            (116, 40, 19)
        ]
        
        self.ingame_hud= [None, "inventory"]
        
        self.pause_sub_hud= [None, "settings", "pause", "pause", "quit_warning"]
        

        # Player
        self.player = {
            "x": 18*8, #156*8-128,
            "y": 52*8, #200*8-128,
            "x_spirit": 100,
            "y_spirit": 100,
            "vx": 0,
            "vy": 0,
            "hp": 100,
            "faith": 100,
            "inventory": [None, "sword", None, "sword", None, None, None, None, "sword", None, None, None],
            "active_slots": [None, "light_bulb", "sword"],
            "anim": 0,  # animation frame
            "immortality": False,
            "immortality_start_frame": 0,
            "cooldown": False,
            "cooldown_start_frame": 0,
            "active_attack": None,
            "slot_at_mouse": [None, None], # [ui_of_slot, slot_id]
            "selected_slot": [None, None]  # [ui_of_slot, slot_id]
        }

        # World
        self.state = STATE_REAL
        self.portals = [
            {"x": 32, "y": 32, "purified": False, "type": "portal"},
            {"x": 96, "y": 96, "purified": False, "type": "portal"},
            {"x": 410, "y": 1304, "purified": False, "type": "lighthouse"},
            {"x": 1086, "y": 1444, "purified": False, "type": "lighthouse"},
            {"x": 1464, "y": 1082, "purified": False, "type": "lighthouse"},
            {"x": 528, "y": 544, "purified": False, "type": "mansion"},
            {"x": 604, "y": 460, "purified": False, "type": "mine"},
            {"x": 402, "y": 928, "purified": False, "type": "mine"},
            {"x": 454, "y": 726, "purified": False, "type": "mine"}
        ]
        self.attack_ui_slot= [
            (75-56, 82-56),
            (94-56, 82-56),
            (113-56, 82-56)
        ]
        self.attack_ui= {
            "sword": {"type": "closed", "x": 16, "y": 112},
            "light_bulb": {"type": "ranged", "x": 0, "y": 112}
        }
        self.tile_type= {
            "no_collision_terrain": None,
            "terrain": [1, 13],
            "sign": [4, 3],
            "forest": [0, 3],
            "path": None,
            "water": [0, 1, 5, 12],
            "wood_bridge": [0, 1, 5],
            "brick_bridge": [0, 1, 5],
            "graveyard": [0, 1, 13],
            "ice": None
        }
        self.tile_id_collision= {
            'no_collision_terrain': [(0, 0), (19, 0), (20, 0), (19, 1), (20, 1), (17, 2), (19, 2), (20, 2), (17, 3), (18, 3), (19, 3), (20, 3), (17, 4), (18, 4), (19, 4), (20, 4), (21, 4), (17, 5), (18, 5), (19, 5), (20, 5), (21, 5), (17, 6), (18, 6), (19, 6), (20, 6), (21, 6), (5, 11), (13, 11), (15, 11), (16, 11), (3, 13), (4, 13), (5, 13), (6, 13), (8, 13), (14, 13), (14, 14), (13, 15), (14, 15), (15, 15), (16, 15), (30, 30), (31, 28)],
            'terrain': [(21, 0), (22, 0), (23, 0), (24, 0), (25, 0), (26, 0), (21, 1), (22, 1), (23, 1), (24, 1), (25, 1), (26, 1), (14, 2), (21, 2), (22, 2), (23, 2), (24, 2), (21, 3), (22, 3), (23, 3), (24, 3), (22, 6), (23, 6), (26, 6), (27, 6), (11, 7), (17, 7), (18, 7), (19, 7), (20, 7), (21, 7), (22, 7), (23, 7), (29, 7), (17, 8), (18, 8), (19, 8), (20, 8), (21, 8), (22, 8), (23, 8), (17, 9), (18, 9), (19, 9), (20, 9), (17, 10), (18, 10), (19, 10), (20, 10), (31, 29)],
            'sign': [(2, 13), (2, 14), (2, 15)],
            'forest': [(22, 4), (23, 4), (24, 4), (25, 4), (22, 5), (23, 5), (24, 5), (25, 5), (24, 6), (25, 6), (24, 7), (25, 7), (24, 8), (25, 8), (22, 9), (23, 9), (24, 9), (25, 9), (22, 10), (23, 10), (31, 30)],
            'path': [(8, 4), (11, 4), (8, 5), (11, 5), (7, 6), (8, 6), (9, 6), (11, 6), (6, 7), (9, 7), (10, 7), (12, 7), (6, 9), (7, 9), (8, 9), (21, 9), (4, 10), (5, 10), (21, 10), (24, 10), (25, 10), (26, 10), (27, 10), (29, 10), (4, 11), (17, 11), (18, 11), (19, 11), (20, 11), (21, 11), (22, 11), (23, 11), (24, 11), (25, 11), (26, 11), (27, 11), (28, 11), (29, 11), (4, 12), (5, 12), (6, 12), (7, 12), (17, 12), (18, 12), (19, 12), (20, 12), (21, 12), (22, 12), (23, 12), (24, 12), (25, 12), (26, 12), (27, 12), (28, 12), (29, 12), (7, 13), (16, 13), (17, 13), (18, 13), (19, 13), (20, 13), (21, 13), (22, 13), (23, 13), (24, 13), (25, 13), (26, 13), (27, 13), (28, 13), (29, 13), (3, 14), (4, 14), (5, 14), (7, 14), (16, 14), (17, 14), (18, 14), (19, 14), (20, 14), (21, 14), (22, 14), (23, 14), (24, 14), (25, 14), (26, 14), (27, 14), (28, 14), (29, 14), (3, 15), (4, 15), (5, 15), (17, 15), (18, 15), (19, 15), (20, 15), (21, 15), (22, 15), (23, 15), (24, 15), (25, 15), (26, 15), (27, 15), (28, 15), (29, 15)],
            'water': [(9, 0), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0), (17, 0), (18, 0), (9, 1), (10, 1), (11, 1), (12, 1), (13, 1), (14, 1), (15, 1), (16, 1), (17, 1), (18, 1), (9, 2), (10, 2), (11, 2), (12, 2), (13, 2), (15, 2), (16, 2), (18, 2), (9, 3), (10, 3), (11, 3), (12, 3), (13, 3), (14, 3), (15, 3), (16, 3), (12, 4), (13, 4), (14, 4), (15, 4), (16, 4), (12, 5), (15, 5), (16, 5), (15, 6), (16, 6), (28, 6), (15, 7), (16, 7), (26, 7), (27, 7), (28, 7), (9, 8), (10, 8), (11, 8), (12, 8), (13, 8), (14, 8), (15, 8), (16, 8), (26, 8), (27, 8), (28, 8), (29, 8), (9, 9), (10, 9), (11, 9), (12, 9), (13, 9), (14, 9), (15, 9), (16, 9), (26, 9), (27, 9), (28, 9), (29, 9), (6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10), (28, 10), (6, 11), (7, 11), (8, 11), (9, 11), (10, 11), (11, 11), (8, 12), (9, 12), (10, 12), (11, 12), (6, 14), (6, 15), (7, 15), (30, 29)],
            'wood_bridge': [(10, 6), (6, 8), (9, 13), (10, 13), (11, 13), (12, 13), (12, 14), (12, 15)],
            'brick_bridge': [(9, 4), (10, 4), (9, 5), (10, 5), (13, 5), (14, 5), (12, 6), (13, 6), (14, 6), (7, 7), (8, 7), (13, 7), (14, 7), (7, 8), (8, 8)],
            'graveyard': [(12, 10), (13, 10), (14, 10), (15, 10), (16, 10), (12, 11), (14, 11), (12, 12), (13, 12), (14, 12), (15, 12), (16, 12), (13, 13), (15, 13), (13, 14), (15, 14)],
            'ice': [(27, 0), (28, 0), (29, 0), (27, 1), (28, 1), (29, 1), (25, 2), (26, 2), (27, 2), (28, 2), (29, 2), (25, 3), (26, 3), (27, 3), (28, 3), (29, 3), (26, 4), (27, 4), (28, 4), (29, 4), (26, 5), (27, 5), (28, 5), (29, 5), (29, 6), (31, 27)]
        }
        self.tree_id= {"1": 0, "2": 16, "3": 32, "4": 48, "5": 64, "6": 80}
        self.cactus_id= {"1": 96}
        self.rock_id= {"1": 64, "2": 72, "3": 80, "4": 88}
        self.bush_id= {"1": 64, "2": 72, "3": 80, "4": 88}
        self.snow_tree_id= {"1": 0, "2": 16, "3": 32}
        self.snow_bush_id= {"1": 0, "2": 8, "3": 16, "4": 24}
        self.snow_rock_id= {"1": 0, "2": 8, "3": 16, "4": 24}
        self.props= []
        for i in range(1736):
            self.props+= [[]]

        
        for tile_y in range(240):
            for tile_x in range(200):
                
                if pyxel.tilemaps[0].pget(tile_x, tile_y)==(31,30):
                    for i in range(1):
                        self.props[tile_y*8+random.randint(1,7)]+= [["tree", tile_x*8+random.randint(1,7), str(random.randint(1,6))]]
                
                elif pyxel.tilemaps[0].pget(tile_x, tile_y)==(30,27):
                    for i in range(random.choice([0,1])):
                        self.props[tile_y*8+random.randint(1,7)]+= [["tree", tile_x*8+random.randint(1,7), str(random.randint(1,6))]]
                        
                elif pyxel.tilemaps[0].pget(tile_x, tile_y)==(0,0):
                    for i in range(random.choice([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1])):
                        tmp= random.randint(1, 3)
                        if tmp==1:
                            self.props[tile_y*8+random.randint(1,7)]+= [["tree", tile_x*8+random.randint(1,7), str(random.randint(1,6))]]
                        elif tmp==2:
                            self.props[tile_y*8+random.randint(1,7)]+= [["bush", tile_x*8+random.randint(1,7), str(random.randint(1,4))]]
                        else:
                            self.props[tile_y*8+random.randint(1,7)]+= [["rock", tile_x*8+random.randint(1,7), str(random.randint(1,4))]]
                        
                elif pyxel.tilemaps[0].pget(tile_x, tile_y)==(30,30):
                    for i in range(random.choice([0,0,0,0,0,0,0,0,0,0,1])):
                        self.props[tile_y*8+random.randint(1,7)]+= [["cactus", tile_x*8+random.randint(1,7), str(random.randint(1,1))]]
                        
                elif pyxel.tilemaps[0].pget(tile_x, tile_y)==(30,28):
                    for i in range(random.choice([0,0,0,0,0,0,1])):
                        self.props[tile_y*8+random.randint(1,7)]+= [["mountain", tile_x*8+random.randint(1,7), str(random.randint(1,1))]]
                        
                elif pyxel.tilemaps[0].pget(tile_x, tile_y)==(31,28):
                    for i in range(random.choice([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1])):
                        tmp= random.randint(1, 3)
                        if tmp==1:
                            self.props[tile_y*8+random.randint(1,7)]+= [["snow_tree", tile_x*8+random.randint(1,7), str(random.randint(1,3))]]
                        elif tmp==2:
                            self.props[tile_y*8+random.randint(1,7)]+= [["snow_bush", tile_x*8+random.randint(1,7), str(random.randint(1,4))]]
                        else:
                            self.props[tile_y*8+random.randint(1,7)]+= [["snow_rock", tile_x*8+random.randint(1,7), str(random.randint(1,4))]]
        
        

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
        if self.ingame_hud.count(self.hud)==1:
            self.update_player()

            if self.state == STATE_REAL:
                self.update_real()
            else:
                self.update_spirit()
        else:
            self.update_outofgame_ui()

    def update_player(self):
        move = ((pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT)) - (pyxel.btn(pyxel.KEY_Q) or pyxel.btn(pyxel.KEY_LEFT)),
                (pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN)) - (pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.KEY_UP)))
        
        if self.state == STATE_REAL:
            player_x= self.player["x"]
            player_y= self.player["y"]
        else:
            player_x= self.player["x_spirit"]
            player_y= self.player["y_spirit"]
        
        # temporary if statement for something that I didn't write yet
        if self.state==STATE_REAL:
            tile_of_player= pyxel.tilemaps[0].pget((player_x+move[0]* 2)//8+16, (player_y+move[1]* 2)//8+16)
            for type_of_tile in self.tile_type:
                if self.tile_id_collision[type_of_tile].count(tile_of_player)==1:
                    if self.tile_type[type_of_tile]!=None:
                        if self.tile_type[type_of_tile].count(pyxel.image(0).pget(tile_of_player[0]*8+(player_x+move[0] * 2)%8+move[0] * 1, tile_of_player[1]*8+(player_y+move[1] * 2)%8+move[1] * 1))==1:
                            move= (0,0)
                        
        
        self.player["vx"] = move[0] * 1
        self.player["vy"] = move[1] * 1
        
        if self.state == STATE_REAL:
            #                                      v : taille de la map
            self.player["x"] = max(-WIDTH//2, min(1596, player_x + self.player["vx"]))
            self.player["y"] = max(-HEIGHT//2, min(1916, player_y + self.player["vy"]))
        else:
            #                                      v : taille de la map
            self.player["x_spirit"] = max(-WIDTH//2, min(1596, player_x + self.player["vx"]))
            self.player["y_spirit"] = max(-HEIGHT//2, min(1916, player_y + self.player["vy"]))
        
        
        
        
        if self.player["immortality"]==True and pyxel.frame_count-self.player["immortality_start_frame"]>15:
            self.player["immortality"]= False

        if self.player["cooldown"]==True and pyxel.frame_count-self.player["cooldown_start_frame"]>6:
            self.player["cooldown"]= False
        else:
            if pyxel.mouse_wheel!=0 and self.state == STATE_SPIRIT:
                self.player["active_attack"]= self.player["active_slots"][(self.player["active_slots"].index(self.player["active_attack"])+pyxel.mouse_wheel)%3]

        if pyxel.btnp(pyxel.KEY_E, 15, 1):
            if self.hud==None:
                self.hud= "inventory"
            else:
                self.hud= None
                self.player["slot_at_mouse"]= [None, None]
                self.player["selected_slot"]= [None, None]
        
        if pyxel.btnp(pyxel.KEY_ESCAPE, 15, 1):
            if self.hud==None:
                self.hud= "pause"
            else:
                self.hud= None
                self.player["slot_at_mouse"]= [None, None]
                self.player["selected_slot"]= [None, None]
        
        if self.hud=="inventory":
            self.player["slot_at_mouse"]= [None, None]
            
            for i in range(len(self.player["inventory"])):
                if pyxel.mouse_x>77+(i%4)*19 and pyxel.mouse_x<94+(i%4)*19 and pyxel.mouse_y>147+(i//4)*19 and pyxel.mouse_y<164+(i//4)*19:
                    self.player["slot_at_mouse"]= ["inventory", i]
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, 15, 1):
                        if self.player["selected_slot"]==[None, None]:
                            self.player["selected_slot"]= ["inventory", i]
                        else:
                            selected_slot_id, selected_slot_in= self.player["selected_slot"][1], self.player["selected_slot"][0]
                            slot_at_mouse_id, slot_at_mouse_in= self.player["slot_at_mouse"][1], self.player["slot_at_mouse"][0]
                            self.player[selected_slot_in][selected_slot_id], self.player[slot_at_mouse_in][slot_at_mouse_id]= self.player[slot_at_mouse_in][slot_at_mouse_id], self.player[selected_slot_in][selected_slot_id]
                            self.player["selected_slot"]= [None, None]
                            if self.player["active_slots"].count(self.player["active_attack"])==0:
                                self.player["active_attack"]= None
                    break
            
            for i in range(3):
                if pyxel.mouse_x>159 and pyxel.mouse_x<177 and pyxel.mouse_y>147+i*19 and pyxel.mouse_y<164+i*19:
                    self.player["slot_at_mouse"]= ["active_slots", i]
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, 15, 1):
                        if self.player["selected_slot"]==[None, None]:
                            self.player["selected_slot"]= ["active_slots", i]
                        else:
                            selected_slot_id, selected_slot_in= self.player["selected_slot"][1], self.player["selected_slot"][0]
                            slot_at_mouse_id, slot_at_mouse_in= self.player["slot_at_mouse"][1], self.player["slot_at_mouse"][0]
                            self.player[selected_slot_in][selected_slot_id], self.player[slot_at_mouse_in][slot_at_mouse_id]= self.player[slot_at_mouse_in][slot_at_mouse_id], self.player[selected_slot_in][selected_slot_id]
                            self.player["selected_slot"]= [None, None]
                            if self.player["active_slots"].count(self.player["active_attack"])==0:
                                self.player["active_attack"]= None
                    break
        
        # animation du joueur
        if move != (0, 0):
            if pyxel.frame_count % 10 == 0:
                self.player["anim"] = 1 - self.player["anim"]
    
    def update_outofgame_ui(self):
        self.player["selected_slot"]= [None, None]
        self.player["slot_at_mouse"]= [None, None]
        if pyxel.btnp(pyxel.KEY_ESCAPE, 15, 1):
            self.hud= None
        if self.hud=="pause":
            for i in range(len(self.pause_ui_text_id)):
                if pyxel.mouse_x>8 and pyxel.mouse_x<12+self.pause_ui_text_id[i][2] and pyxel.mouse_y>18+i*30 and pyxel.mouse_y<30+i*30:
                    self.player["slot_at_mouse"]= ["pause", i]
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, 15, 1):
                        if i==0:
                            self.hud= None
                            self.player["selected_slot"]= [None, None]
                            self.player["slot_at_mouse"]= [None, None]
                        else:
                            self.player["selected_slot"]= ["pause", i]
                    break
                
            if self.player["selected_slot"]!=[None, None]:
                self.hud= self.pause_sub_hud[self.player["selected_slot"][1]]
                self.player["slot_at_mouse"]= [None, None]
        
        elif self.hud=="quit_warning":
            for i in range(2):
                if pyxel.mouse_x>93+i*48 and pyxel.mouse_x<115+i*48 and pyxel.mouse_y>131 and pyxel.mouse_y<145:
                    self.player["slot_at_mouse"]= ["quit_warning", i]
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, 15, 1):
                        if i==0:
                            pyxel.quit()
                        else:
                            self.hud="pause"
                            self.player["selected_slot"]= [None, None]
                            self.player["slot_at_mouse"]= [None, None]
                    break
        
    
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
            self.player["faith"] -= 1
            if self.player["faith"] <= 0:
                self.exit_spirit(failed=True)

        # -------------------------------
        # ATTAQUE (LEFT CLICK)
        # -------------------------------
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.player["cooldown"]==False:
            if self.player["active_attack"]!=None:
                if self.attack_ui[self.player["active_attack"]]["type"]=="ranged":
                    self.player["cooldown"]= True
                    self.player["cooldown_start_frame"]= pyxel.frame_count
                    dif_x= (self.player["x_spirit"])-pyxel.mouse_x
                    dif_y= (self.player["y_spirit"])-pyxel.mouse_y
                    # défaut : tir vers la droite
                    if dif_x == 0 and dif_y == 0:
                        dx= 1
                        dy= 0
                    elif dif_x==0:
                        dx= 0
                        dy= -dif_y/abs(dif_y)
                    elif dif_y==0:
                        dx= -dif_x/abs(dif_x)
                        dy=0
                    elif abs(dif_x) > abs(dif_y):
                        dx= -dif_x/abs(dif_x)
                        dy= -dif_y/abs(dif_x)
                    else:
                        dx= -dif_x/abs(dif_y)
                        dy= -dif_y/abs(dif_y)

                    self.projectiles.append({
                        "x": self.player["x_spirit"],
                        "y": self.player["y_spirit"],
                        "dx": dx,
                        "dy": dy,
                        "spd": 3,
                        "life": 40
                    })
                
                elif self.attack_ui[self.player["active_attack"]]["type"]=="closed":
                    self.player["cooldown_start_frame"]= pyxel.frame_count
                    for m in self.monsters:
                        if self.player["x_spirit"]>pyxel.mouse_x:
                            clipping= -16
                        else:
                            clipping= 0
                        tmp= {"x_spirit": self.player["x_spirit"]+14+clipping*1.625, "y_spirit": self.player["y_spirit"]}
                    
                    
                        if self.dist(tmp, m, "x_spirit", "y_spirit") < 12:
                            m["hp"] -= 0.5
                            self.spawn_hit_particles(m["x"], m["y"])
                

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
            dx = 1 if self.player["x_spirit"] > m["x"] else -1
            dy = 1 if self.player["y_spirit"] > m["y"] else -1
            m["x"] += dx * m["spd"]
            m["y"] += dy * m["spd"]

            m["anim"] = (pyxel.frame_count // 10) % 2

            # contact joueur
            if self.dist(self.player, m, "x_spirit", "y_spirit") < 6:
                if self.player["immortality"]==False:
                    if self.player["hp"]>0:
                        self.player["hp"] -= 10
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
            if not n["purified"] and self.dist(self.player, n, "x_spirit", "y_spirit") < 8:
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
            {"x": 20, "y": 20, "hp": 3, "spd": 0.5, "anim": 0, "stun": False, "stun_start_frame": 0, "stun_type": None},
            {"x": 110, "y": 100, "hp": 4, "spd": 0.6, "anim": 0, "stun": False, "stun_start_frame": 0, "stun_type": None}
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
    
    def draw_props(self):
        self.props[self.player["y"]+124]+= [["player", 124, 1]]
        for y in range(len(self.props)):
            for prop in self.props[y]:
                if prop[0]=="tree":
                    pyxel.blt(prop[1]-self.player["x"]-8, y-self.player["y"]-10, 0, 240, self.tree_id[prop[2]], 16, 16, 7)
                elif prop[0]=="bush":
                    pyxel.blt(prop[1]-self.player["x"]-8, y-self.player["y"], 0, self.bush_id[prop[2]], 112, 8, 8, 7)
                elif prop[0]=="rock":
                    pyxel.blt(prop[1]-self.player["x"]-8, y-self.player["y"], 0, self.rock_id[prop[2]], 120, 8, 8, 7)
                elif prop[0]=="snow_tree":
                    pyxel.blt(prop[1]-self.player["x"]-8, y-self.player["y"]-10, 0, 16, self.snow_tree_id[prop[2]], 16, 16, 15)
                elif prop[0]=="snow_bush":
                    pyxel.blt(prop[1]-self.player["x"]-8, y-self.player["y"], 0, 32, self.snow_bush_id[prop[2]], 8, 8, 15)
                elif prop[0]=="snow_rock":
                    pyxel.blt(prop[1]-self.player["x"]-8, y-self.player["y"], 0, 40, self.snow_rock_id[prop[2]], 8, 8, 15)
                elif prop[0]=="cactus":
                    pyxel.blt(prop[1]-self.player["x"]-8, y-self.player["y"]-10, 0, 240, self.cactus_id[prop[2]], 16, 16, 7)
                elif prop[0]=="mountain":
                    pyxel.blt(prop[1]-self.player["x"]-8, y-self.player["y"]-10, 2, 112, 0, 64, 32, 2)
                elif prop[0]=="player":
                    pyxel.blt(prop[1], y-self.player["y"], 0, 48, 0, 8, 8, 7)
        self.props[self.player["y"]+124].pop()
            
    # -------------------------------

    def draw_real(self):
        pyxel.cls(1)
        
        pyxel.bltm(0, 0, 0, self.player["x"], self.player["y"], WIDTH, HEIGHT)
        
        self.draw_props()
                
        # Aura animée autour des portails
        for p in self.portals:
            if not p["purified"]:
                if p["type"]=="portal":
                    r = 6 + (pyxel.frame_count % 8)
                    pyxel.circ(p["x"]-self.player["x"]+WIDTH//2, p["y"]-self.player["y"]+HEIGHT//2, r, 13)
                elif p["type"]=="lighthouse":
                    pass
                elif p["type"]=="mansion":
                    pass

        # Portails
        for p in self.portals:
            if p["type"]=="portal":
                col = 11 if p["purified"] else 2
                pyxel.circ(p["x"]-self.player["x"]+WIDTH//2, p["y"]-self.player["y"]+HEIGHT//2, 3, col)
            
            elif p["type"]=="lighthouse":
                pyxel.blt(p["x"]-self.player["x"]+WIDTH//2, p["y"]-self.player["y"]+HEIGHT//2, 2, 0, 0, 47, 111, 4)
            
            elif p["type"]=="mansion":
                pyxel.blt(p["x"]-self.player["x"]+WIDTH//2, p["y"]-self.player["y"]+HEIGHT//2, 2, 48, 0, 64, 40, 8)
                
            elif p["type"]=="mine":
                pyxel.blt(p["x"]-self.player["x"]+WIDTH//2, p["y"]-self.player["y"]+HEIGHT//2, 2, 48, 40, 19, 15, 8)

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
        pyxel.cls(9)

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
            
        # Joueur
        col = 14 if self.player["anim"] == 0 else 7
        #pyxel.circ(self.player["x"], self.player["y"], 3, col)
        pyxel.blt(self.player["x_spirit"]-8, self.player["y_spirit"]-8, 1, 80, 0, 16, 16, 7)
        
        if self.player["active_attack"]!=None:
            if self.attack_ui[self.player["active_attack"]]["type"]=="closed":
                clipping= 0
            
                if self.player["x_spirit"]>pyxel.mouse_x and self.ingame_hud.count(self.hud)==1:
                    clipping= -16
                
                if pyxel.frame_count-self.player["cooldown_start_frame"]<18:
                    tmp= (pyxel.frame_count-self.player["cooldown_start_frame"])//3
                    pyxel.blt(self.player["x_spirit"]+6+clipping*1.625, self.player["y_spirit"]-6, 1, 80+(tmp%3)*16, 32+(tmp//3)*16-clipping*2, 16, 16, 7)
                else:
                    pyxel.blt(self.player["x_spirit"]+6+clipping*1.625, self.player["y_spirit"]-6, 1, 80, 32-clipping*2, 16, 16, 7)
        
        for h in self.particles:
            pyxel.pset(h["x"], h["y"], 7)
            
    
        

    # -------------------------------

    def draw_ui(self):
        pyxel.blt(WIDTH-112, HEIGHT-60, 2, 56, 56, 104, 56, 7) # main ui
        if self.player["hp"]>0:
            pyxel.blt(WIDTH-107, HEIGHT-18, 2, 61, 114, 66-(100-self.player["hp"])/100*65, 8, 7) # health
        if self.player["faith"]>0:
            pyxel.blt(WIDTH-40, HEIGHT-52+(100-self.player["faith"])/100*44, 2, 160, 64+(100-self.player["faith"])/100*44, 32, 44-(100-self.player["faith"])/100*44, 7) # faith
        
        if self.hud!=None:
            if self.hud=="inventory":
                
                pyxel.blt(74, 144, 2, 0, 152, 108, 62, 0)
                
                for i in range(3):
                    attack_name= self.player["active_slots"][i]
                    if attack_name!=None:
                        item= self.attack_ui[attack_name]
                        pyxel.blt(160, 148+19*i, 2, item["x"], item["y"], 16, 16, 7)
                for i in range(len(self.player["inventory"])):
                    attack_name= self.player["inventory"][i]
                    if attack_name!=None:
                        item= self.attack_ui[attack_name]
                        pyxel.blt(78+(i%4)*19, 148+(i//4)*19, 2, item["x"], item["y"], 16, 16, 7)
                
                if self.player["selected_slot"]!=[None, None]:
                    if self.player["selected_slot"][0]=="inventory":
                        pyxel.blt(75+(self.player["selected_slot"][1]%4)*19, 145+(self.player["selected_slot"][1]//4)*19, 2, 24, 128, 24, 24, 4)
                    elif self.player["selected_slot"][0]=="active_slots":
                        pyxel.blt(71+86, 145+self.player["selected_slot"][1]*19, 2, 24, 128, 24, 24, 4)
                
                if self.player["slot_at_mouse"]!=[None, None]:
                    if self.player["slot_at_mouse"][0]=="inventory":
                        #pyxel.rectb(78+(self.player["slot_at_mouse"]%4)*19, 148+(self.player["slot_at_mouse"]//4)*19, 16, 16, 8)
                        pyxel.blt(75+(self.player["slot_at_mouse"][1]%4)*19, 145+(self.player["slot_at_mouse"][1]//4)*19, 2, 0, 128, 24, 24, 4)
                    elif self.player["slot_at_mouse"][0]=="active_slots":
                        pyxel.blt(71+86, 145+self.player["slot_at_mouse"][1]*19, 2, 0, 128, 24, 24, 4)
            
            
            elif self.hud=="pause":
                pyxel.rect(0, 0, 75, HEIGHT, 0)
                for i in range(HEIGHT//8):
                    pyxel.blt(75, 0+i*8, 2, 112, 32, 47, 8, 7)
                for i in range(len(self.pause_ui_text_id)):
                    pyxel.blt(10, 20+i*30, 2, self.pause_ui_text_id[i][0], self.pause_ui_text_id[i][1], self.pause_ui_text_id[i][2], 8, 3)
                if self.player["slot_at_mouse"]!=[None, None]:
                    slot_id= self.player["slot_at_mouse"][1]
                    pyxel.rectb(9, 18+slot_id*30, self.pause_ui_text_id[slot_id][2]+3, 13, 5)
                    pyxel.trib(8, 19+slot_id*30, 8, 29+slot_id*30, 3, 24+slot_id*30, 5)
                    pyxel.trib(self.pause_ui_text_id[slot_id][2]+12, 19+slot_id*30, self.pause_ui_text_id[slot_id][2]+12, 29+slot_id*30, self.pause_ui_text_id[slot_id][2]+17, 24+slot_id*30, 5)
                    pyxel.tri(9, 19+slot_id*30, 9, 29+slot_id*30, 4, 24+slot_id*30, 12)
                    pyxel.tri(self.pause_ui_text_id[slot_id][2]+11, 19+slot_id*30, self.pause_ui_text_id[slot_id][2]+11, 29+slot_id*30, self.pause_ui_text_id[slot_id][2]+16, 24+slot_id*30, 12)
                    pyxel.rect(9, 19+slot_id*30, self.pause_ui_text_id[slot_id][2]+2, 11, 12)
                    pyxel.blt(10, 20+slot_id*30, 2, self.pause_ui_text_id[slot_id][0]+64, self.pause_ui_text_id[slot_id][1], self.pause_ui_text_id[slot_id][2], 8, 3)
            
            elif self.hud=="quit_warning":
                pyxel.rect(0, 0, 75, HEIGHT, 0)
                for i in range(HEIGHT//8):
                    pyxel.blt(75, 0+i*8, 2, 112, 32, 47, 8, 7)
                for i in range(len(self.pause_ui_text_id)):
                    pyxel.blt(10, 20+i*30, 2, self.pause_ui_text_id[i][0], self.pause_ui_text_id[i][1], self.pause_ui_text_id[i][2], 8, 3)
                    
                for i in range(12):
                    pyxel.blt(80+i*8, 104, 2, 184, 0, 8, 8)
                    pyxel.blt(80+i*8, 112+4*8, 2, 184, 16, 8, 8)
                    
                for i in range(4):
                    pyxel.blt(72, 112+i*8, 2, 176, 8, 8, 8)
                    pyxel.blt(80+12*8, 112+i*8, 2, 192, 8, 8, 8)
                    
                for x in range(2):
                    for y in range(2):
                        pyxel.blt(72+x*104, 104+y*40, 2, 176+x*16, 0+y*16, 8, 8, 0)
                        
                pyxel.rect(80, 112, 96, 32, 1)
                
                pyxel.blt(78, 112, 2, 0, 216, 104, 16, 3)
                
                if self.player["slot_at_mouse"]!=[None, None]:
                    slot_id= self.player["slot_at_mouse"][1]
                    pyxel.rectb(95+slot_id*48, 132, 16, 13, 5)
                    pyxel.trib(94+slot_id*48, 133, 94+slot_id*48, 143, 89+slot_id*48, 138, 5)
                    pyxel.trib(111+slot_id*48, 133, 111+slot_id*48, 143, 116+slot_id*48, 138, 5)
                    pyxel.tri(95+slot_id*48, 133, 95+slot_id*48, 143, 90+slot_id*48, 138, 12)
                    pyxel.tri(110+slot_id*48, 133, 110+slot_id*48, 143, 115+slot_id*48, 138, 12)
                    pyxel.rect(95+slot_id*48, 133, 16, 11, 12)
                    
                for i in range(2):
                    pyxel.blt(96+i*50, 134, 2, 32-16*i, 248, 16-5*i, 8, 15)
            
            elif self.hud=="settings":
                for i in range(20):
                    pyxel.blt(48+i*8, 48, 2, 184, 0, 8, 8)
                    pyxel.blt(48+i*8, 56+18*8, 2, 184, 16, 8, 8)
                    
                for i in range(18):
                    pyxel.blt(40, 56+i*8, 2, 176, 8, 8, 8)
                    pyxel.blt(48+20*8, 56+i*8, 2, 192, 8, 8, 8)
                    
                for x in range(2):
                    for y in range(2):
                        pyxel.blt(40+x*168, 48+y*152, 2, 176+x*16, 0+y*16, 8, 8, 0)
                        
                pyxel.rect(48, 56, 160, 144, 1)
                    
        for i in range(3):
            attack_name= self.player["active_slots"][i]
            if attack_name!=None:
                item= self.attack_ui[attack_name]
                pyxel.blt(WIDTH-93+19*i, HEIGHT-34, 2, item["x"], item["y"], 16, 16, 7)
        
            if self.state == STATE_SPIRIT:
                index= (self.player["active_slots"].index(self.player["active_attack"])+(pyxel.mouse_wheel*(int(self.ingame_hud.count(self.hud)==1))))%3
                pyxel.blt(WIDTH-112-3+self.attack_ui_slot[index][0], HEIGHT-60-3+self.attack_ui_slot[index][1], 2, 0, 128, 24, 24, 4)
    
        #pyxel.text(5, HEIGHT - 15, f"HP:{self.player['hp']}", 7)
        #pyxel.text(50, HEIGHT - 15, f"Faith:{self.player['faith']}", 7)

        if self.memory_fragments:
            pyxel.text(5, 5, self.memory_fragments[-1], 6)

    # -------------------------------

    @staticmethod
    def dist(a, b, base_x= "x", base_y= "y"):
        return ((a[base_x] - b["x"]) ** 2 + (a[base_y] - b["y"]) ** 2) ** 0.5


Game()




