import pyxel
import math
import random

WIDTH, HEIGHT = 256, 256

STATE_REAL = 0
STATE_SPIRIT = 1
STATE_SPIRIT_SUB_ZONE = 2


class Game:
    def __init__(self):
        pyxel.init(
            WIDTH,
            HEIGHT,
            title="Broken Places",
            fps=30,
            quit_key=pyxel.KEY_RCTRL,
            display_scale=3,
        )
        pyxel.load("5.pyxres")
        pyxel.mouse(True)
        self.temp = []
        self.hud = None
        self.qol_loot_ui = []  # {"type": ..., "obtention_frame": ...}
        self.settings = False
        self.pause_ui_text_id = [
            (107, 48, 29),
            (72, 48, 35),
            (72, 40, 63),
            (72, 40, 23),
            (116, 40, 19),
        ]

        self.ingame_hud = [None, "inventory"]

        self.pause_sub_hud = [None, "settings", "pause", "pause", "quit_warning"]
        self.path_map = []

        # Player
        self.player = {
            "x": 38 * 8 - 128,
            "y": 18 * 8 - 128,
            "x_spirit": 100,
            "y_spirit": 100,
            "vx": 0,
            "vy": 0,
            "hp": 100,
            "faith": 100,
            "inventory": [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            "active_slots": ["sword", None, None],
            "anim": 0,  # animation frame
            "portal_id": None,
            "immortality": False,
            "immortality_start_frame": 0,
            "cooldown": False,
            "cooldown_start_frame": 0,
            "active_attack": "sword",
            "slot_at_mouse": [None, None],  # [ui_of_slot, slot_id]
            "selected_slot": [None, None],  # [ui_of_slot, slot_id]
        }

        # World
        self.state = STATE_REAL
        self.state_entry_frame = 0
        self.portals = [
            {
                "x": 144,
                "y": 416,
                "purified": False,
                "type": "portal",
                "start_time": 0,
                "state": STATE_SPIRIT,
            },
            {
                "x": 123 * 8 - 128,
                "y": 128 * 8 - 64,
                "purified": False,
                "type": "portal",
                "start_time": 0,
                "state": STATE_SPIRIT,
            },
            {
                "x": 410,
                "y": 1304,
                "purified": True,
                "type": "lighthouse",
                "start_time": 0,
                "state": STATE_SPIRIT_SUB_ZONE,
            },
            {
                "x": 1086,
                "y": 1444,
                "purified": True,
                "type": "lighthouse",
                "start_time": 0,
                "state": STATE_SPIRIT_SUB_ZONE,
            },
            {
                "x": 1464,
                "y": 1082,
                "purified": True,
                "type": "lighthouse",
                "start_time": 0,
                "state": STATE_SPIRIT_SUB_ZONE,
            },
            {
                "x": 528,
                "y": 544,
                "purified": True,
                "type": "mansion",
                "start_time": 0,
                "state": STATE_SPIRIT_SUB_ZONE,
            },
            {
                "x": 604,
                "y": 460,
                "purified": True,
                "type": "mine",
                "start_time": 0,
                "state": STATE_SPIRIT_SUB_ZONE,
                "id": 3,
            },
            {
                "x": 402,
                "y": 928,
                "purified": True,
                "type": "mine",
                "start_time": 0,
                "state": STATE_SPIRIT_SUB_ZONE,
                "id": 1,
            },
            {
                "x": 336,
                "y": 304,
                "purified": False,
                "type": "mine",
                "start_time": 0,
                "state": STATE_SPIRIT_SUB_ZONE,
                "id": 0,
            },
            {
                "x": 200,
                "y": 528,
                "purified": False,
                "type": "mine",
                "start_time": 0,
                "state": STATE_SPIRIT_SUB_ZONE,
                "id": 0,
            },
            {
                "x": 454,
                "y": 726,
                "purified": True,
                "type": "mine",
                "start_time": 0,
                "state": STATE_SPIRIT_SUB_ZONE,
                "id": 2,
            },
        ]
        self.mine_path = {
            0: {"x": 128, "y": 128, "l": 640, "h": 512},
            1: {"x": 0, "y": 0, "l": 0, "h": 0},
            2: {"x": 0, "y": 0, "l": 0, "h": 0},
            3: {"x": 0, "y": 0, "l": 0, "h": 0},
        }
        self.mine_exit = [
            {
                "x_real": 200,
                "y_real": 528,
                "x": 26 * 8 - 128,
                "y": 74 * 8 - 128,
                "id": 0,
            },
            {
                "x_real": 336,
                "y_real": 304,
                "x": 90 * 8 - 128,
                "y": 44 * 8 - 128,
                "id": 0,
            },
            {"x_real": 402, "y_real": 928, "x": 0, "y": 0, "id": 1},
            {"x_real": 454, "y_real": 726, "x": 0, "y": 0, "id": 2},
            {"x_real": 604, "y_real": 460, "x": 0, "y": 0, "id": 3},
        ]
        self.effect_ui = {
            "poison_bomb": {"x": 128, "y": 112, "u": 16, "v": 16, "col": 7},
            "cryogenis": {"x": 192, "y": 88, "u": 16, "v": 16, "col": 0},
        }

        self.attack_ui_slot = [
            (75 - 56, 82 - 56),
            (94 - 56, 82 - 56),
            (113 - 56, 82 - 56),
        ]
        self.attack_ui = {
            "sword": {
                "type": "closed",
                "x": 16,
                "y": 112,
                "zone": 1,
                "stun_time": 0,
                "damage_frame": 1,
            },
            "cryogenis": {
                "type": "ranged",
                "x": 0,
                "y": 112,
                "zone": 1,
                "stun_time": 10,
                "damage_frame": 90,
            },
            "poison_bomb": {
                "type": "ranged",
                "x": 32,
                "y": 112,
                "zone": 8,
                "stun_time": 0,
                "damage_frame": 24,
            },
        }

        self.projectile_info_impact = (
            []
        )  # {"type": ..., "x": ..., "y": ..., "impact_frame": ...}

        self.tile_type_spirit_sub = {"no_collision_terrain": None, "terrain": [1, 2, 5]}

        self.tile_id_collision_spirit_sub = {
            "no_collision_terrain": [
                (31, 28),
                (14, 28),
                (15, 28),
                (14, 29),
                (15, 29),
                (14, 30),
                (15, 30),
                (14, 31),
                (15, 31),
                (13, 25),
                (14, 25),
                (13, 26),
                (14, 26),
                (4, 25),
                (8, 18),
                (8, 19),
                (8, 20),
                (8, 21),
                (9, 18),
                (9, 19),
                (9, 20),
                (9, 21),
                (10, 18),
                (10, 19),
                (10, 20),
                (10, 21),
                (11, 18),
                (11, 19),
                (11, 20),
                (11, 21),
                (12, 17),
                (12, 18),
                (13, 17),
                (13, 18),
                (14, 17),
                (14, 18),
                (15, 17),
                (15, 18),
                (12, 22),
                (12, 23),
                (13, 22),
                (13, 23),
                (14, 22),
                (14, 23),
                (15, 22),
                (15, 23),
                (16, 22),
                (16, 23),
                (17, 22),
                (17, 23),
                (16, 24),
                (16, 25),
                (16, 26),
                (16, 27),
                (17, 24),
                (17, 25),
                (17, 26),
                (17, 27),
                (14, 19),
                (14, 20),
                (14, 21),
                (12, 20),
                (13, 20),
                (6, 18),
                (6, 19),
                (7, 18),
                (7, 19),
                (5, 19),
                (6, 20),
            ],
            "terrain": [
                (31, 29),
                (4, 24),
                (8, 22),
                (9, 22),
                (8, 23),
                (9, 23),
                (8, 24),
                (9, 24),
                (8, 25),
                (9, 25),
                (10, 24),
                (10, 25),
                (10, 26),
                (10, 27),
                (11, 24),
                (11, 25),
                (11, 26),
                (11, 27),
                (12, 24),
                (12, 25),
                (12, 26),
                (12, 27),
                (13, 24),
                (13, 25),
                (13, 26),
                (13, 27),
                (14, 24),
                (14, 25),
                (14, 26),
                (14, 27),
                (15, 24),
                (15, 25),
                (15, 26),
                (15, 27),
                (10, 28),
                (10, 29),
                (10, 30),
                (10, 31),
                (11, 28),
                (11, 29),
                (11, 30),
                (11, 31),
                (12, 28),
                (12, 29),
                (12, 30),
                (12, 31),
                (13, 28),
                (13, 29),
                (13, 30),
                (13, 31),
                (6, 30),
                (6, 31),
                (7, 30),
                (7, 31),
                (8, 30),
                (8, 31),
                (9, 30),
                (9, 31),
            ],
        }

        self.tile_type = {
            "no_collision_terrain": None,
            "terrain": [1, 13],
            "sign": [4, 3],
            "forest": [0, 3],
            "path": None,
            "water": [0, 1, 5, 12],
            "wood_bridge": [0, 1, 5],
            "brick_bridge": [0, 1, 5],
            "graveyard": [0, 1, 13],
            "ice": None,
        }
        self.tile_id_collision = {
            "no_collision_terrain": [
                (0, 0),
                (1, 2),
                (0, 4),
                (19, 0),
                (20, 0),
                (19, 1),
                (20, 1),
                (17, 2),
                (19, 2),
                (20, 2),
                (17, 3),
                (18, 3),
                (19, 3),
                (20, 3),
                (17, 4),
                (18, 4),
                (19, 4),
                (20, 4),
                (21, 4),
                (17, 5),
                (18, 5),
                (19, 5),
                (20, 5),
                (21, 5),
                (17, 6),
                (18, 6),
                (19, 6),
                (20, 6),
                (21, 6),
                (5, 11),
                (13, 11),
                (15, 11),
                (16, 11),
                (3, 13),
                (4, 13),
                (5, 13),
                (6, 13),
                (8, 13),
                (14, 13),
                (14, 14),
                (13, 15),
                (14, 15),
                (15, 15),
                (16, 15),
            ],
            "terrain": [
                (0, 2),
                (1, 3),
                (21, 0),
                (22, 0),
                (23, 0),
                (24, 0),
                (25, 0),
                (26, 0),
                (21, 1),
                (22, 1),
                (23, 1),
                (24, 1),
                (25, 1),
                (26, 1),
                (14, 2),
                (21, 2),
                (22, 2),
                (23, 2),
                (24, 2),
                (21, 3),
                (22, 3),
                (23, 3),
                (24, 3),
                (22, 6),
                (23, 6),
                (26, 6),
                (27, 6),
                (11, 7),
                (17, 7),
                (18, 7),
                (19, 7),
                (20, 7),
                (21, 7),
                (22, 7),
                (23, 7),
                (29, 7),
                (17, 8),
                (18, 8),
                (19, 8),
                (20, 8),
                (21, 8),
                (22, 8),
                (23, 8),
                (17, 9),
                (18, 9),
                (19, 9),
                (20, 9),
                (17, 10),
                (18, 10),
                (19, 10),
                (20, 10),
            ],
            "sign": [(5, 7), (5, 8), (5, 9)],
            "forest": [
                (1, 0),
                (22, 4),
                (23, 4),
                (24, 4),
                (25, 4),
                (22, 5),
                (23, 5),
                (24, 5),
                (25, 5),
                (24, 6),
                (25, 6),
                (24, 7),
                (25, 7),
                (24, 8),
                (25, 8),
                (22, 9),
                (23, 9),
                (24, 9),
                (25, 9),
                (22, 10),
                (23, 10),
            ],
            "path": [
                (8, 4),
                (11, 4),
                (8, 5),
                (11, 5),
                (7, 6),
                (8, 6),
                (9, 6),
                (11, 6),
                (6, 7),
                (9, 7),
                (10, 7),
                (12, 7),
                (6, 9),
                (7, 9),
                (8, 9),
                (21, 9),
                (4, 10),
                (5, 10),
                (21, 10),
                (24, 10),
                (25, 10),
                (26, 10),
                (27, 10),
                (29, 10),
                (4, 11),
                (17, 11),
                (18, 11),
                (19, 11),
                (20, 11),
                (21, 11),
                (22, 11),
                (23, 11),
                (24, 11),
                (25, 11),
                (26, 11),
                (27, 11),
                (28, 11),
                (29, 11),
                (4, 12),
                (5, 12),
                (6, 12),
                (7, 12),
                (17, 12),
                (18, 12),
                (19, 12),
                (20, 12),
                (21, 12),
                (22, 12),
                (23, 12),
                (24, 12),
                (25, 12),
                (26, 12),
                (27, 12),
                (28, 12),
                (29, 12),
                (7, 13),
                (16, 13),
                (17, 13),
                (18, 13),
                (19, 13),
                (20, 13),
                (21, 13),
                (22, 13),
                (23, 13),
                (24, 13),
                (25, 13),
                (26, 13),
                (27, 13),
                (28, 13),
                (29, 13),
                (3, 14),
                (4, 14),
                (5, 14),
                (7, 14),
                (16, 14),
                (17, 14),
                (18, 14),
                (19, 14),
                (20, 14),
                (21, 14),
                (22, 14),
                (23, 14),
                (24, 14),
                (25, 14),
                (26, 14),
                (27, 14),
                (28, 14),
                (29, 14),
                (3, 15),
                (4, 15),
                (5, 15),
                (17, 15),
                (18, 15),
                (19, 15),
                (20, 15),
                (21, 15),
                (22, 15),
                (23, 15),
                (24, 15),
                (25, 15),
                (26, 15),
                (27, 15),
                (28, 15),
                (29, 15),
            ],
            "water": [
                (0, 3),
                (9, 0),
                (10, 0),
                (11, 0),
                (12, 0),
                (13, 0),
                (14, 0),
                (15, 0),
                (16, 0),
                (17, 0),
                (18, 0),
                (9, 1),
                (10, 1),
                (11, 1),
                (12, 1),
                (13, 1),
                (14, 1),
                (15, 1),
                (16, 1),
                (17, 1),
                (18, 1),
                (9, 2),
                (10, 2),
                (11, 2),
                (12, 2),
                (13, 2),
                (15, 2),
                (16, 2),
                (18, 2),
                (9, 3),
                (10, 3),
                (11, 3),
                (12, 3),
                (13, 3),
                (14, 3),
                (15, 3),
                (16, 3),
                (12, 4),
                (13, 4),
                (14, 4),
                (15, 4),
                (16, 4),
                (12, 5),
                (15, 5),
                (16, 5),
                (15, 6),
                (16, 6),
                (28, 6),
                (15, 7),
                (16, 7),
                (26, 7),
                (27, 7),
                (28, 7),
                (9, 8),
                (10, 8),
                (11, 8),
                (12, 8),
                (13, 8),
                (14, 8),
                (15, 8),
                (16, 8),
                (26, 8),
                (27, 8),
                (28, 8),
                (29, 8),
                (9, 9),
                (10, 9),
                (11, 9),
                (12, 9),
                (13, 9),
                (14, 9),
                (15, 9),
                (16, 9),
                (26, 9),
                (27, 9),
                (28, 9),
                (29, 9),
                (6, 10),
                (7, 10),
                (8, 10),
                (9, 10),
                (10, 10),
                (11, 10),
                (28, 10),
                (6, 11),
                (7, 11),
                (8, 11),
                (9, 11),
                (10, 11),
                (11, 11),
                (8, 12),
                (9, 12),
                (10, 12),
                (11, 12),
                (6, 14),
                (6, 15),
                (7, 15),
            ],
            "wood_bridge": [
                (10, 6),
                (6, 8),
                (9, 13),
                (10, 13),
                (11, 13),
                (12, 13),
                (12, 14),
                (12, 15),
            ],
            "brick_bridge": [
                (9, 4),
                (10, 4),
                (9, 5),
                (10, 5),
                (13, 5),
                (14, 5),
                (12, 6),
                (13, 6),
                (14, 6),
                (7, 7),
                (8, 7),
                (13, 7),
                (14, 7),
                (7, 8),
                (8, 8),
            ],
            "graveyard": [
                (12, 10),
                (13, 10),
                (14, 10),
                (15, 10),
                (16, 10),
                (12, 11),
                (14, 11),
                (12, 12),
                (13, 12),
                (14, 12),
                (15, 12),
                (16, 12),
                (13, 13),
                (15, 13),
                (13, 14),
                (15, 14),
            ],
            "ice": [
                (1, 1),
                (27, 0),
                (28, 0),
                (29, 0),
                (27, 1),
                (28, 1),
                (29, 1),
                (25, 2),
                (26, 2),
                (27, 2),
                (28, 2),
                (29, 2),
                (25, 3),
                (26, 3),
                (27, 3),
                (28, 3),
                (29, 3),
                (26, 4),
                (27, 4),
                (28, 4),
                (29, 4),
                (26, 5),
                (27, 5),
                (28, 5),
                (29, 5),
                (29, 6),
            ],
        }
        self.tree_id = {"1": 0, "2": 16, "3": 32, "4": 48, "5": 64, "6": 80}
        self.cactus_id = {"1": 96}
        self.rock_id = {"1": 64, "2": 72, "3": 80, "4": 88}
        self.bush_id = {"1": 64, "2": 72, "3": 80, "4": 88}
        self.snow_tree_id = {"1": 0, "2": 16, "3": 32}
        self.snow_bush_id = {"1": 0, "2": 8, "3": 16, "4": 24}
        self.snow_rock_id = {"1": 0, "2": 8, "3": 16, "4": 24}
        self.props = []

        for i in range(1736):
            self.props += [[]]

        for tile_y in range(240):
            for tile_x in range(200):

                if pyxel.tilemaps[0].pget(tile_x, tile_y) == (1, 0):
                    for i in range(1):
                        self.props[tile_y * 8 + random.randint(1, 7)] += [
                            [
                                "tree",
                                tile_x * 8 + random.randint(1, 7),
                                str(random.randint(1, 6)),
                            ]
                        ]

                elif pyxel.tilemaps[0].pget(tile_x, tile_y) == (0, 1):
                    for i in range(random.choice([0, 1])):
                        self.props[tile_y * 8 + random.randint(1, 7)] += [
                            [
                                "tree",
                                tile_x * 8 + random.randint(1, 7),
                                str(random.randint(1, 6)),
                            ]
                        ]

                elif pyxel.tilemaps[0].pget(tile_x, tile_y) == (0, 0):
                    for i in range(
                        random.choice(
                            [
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                1,
                            ]
                        )
                    ):
                        tmp = random.randint(1, 3)
                        if tmp == 1:
                            self.props[tile_y * 8 + random.randint(1, 7)] += [
                                [
                                    "tree",
                                    tile_x * 8 + random.randint(1, 7),
                                    str(random.randint(1, 6)),
                                ]
                            ]
                        elif tmp == 2:
                            self.props[tile_y * 8 + random.randint(1, 7)] += [
                                [
                                    "bush",
                                    tile_x * 8 + random.randint(1, 7),
                                    str(random.randint(1, 4)),
                                ]
                            ]
                        else:
                            self.props[tile_y * 8 + random.randint(1, 7)] += [
                                [
                                    "rock",
                                    tile_x * 8 + random.randint(1, 7),
                                    str(random.randint(1, 4)),
                                ]
                            ]

                elif pyxel.tilemaps[0].pget(tile_x, tile_y) == (0, 4):
                    for i in range(random.choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])):
                        self.props[tile_y * 8 + random.randint(1, 7)] += [
                            [
                                "cactus",
                                tile_x * 8 + random.randint(1, 7),
                                str(random.randint(1, 1)),
                            ]
                        ]

                elif pyxel.tilemaps[0].pget(tile_x, tile_y) == (0, 2):
                    for i in range(random.choice([0, 0, 0, 0, 0, 0, 1])):
                        self.props[tile_y * 8 + random.randint(1, 7)] += [
                            [
                                "mountain",
                                tile_x * 8 + random.randint(1, 7),
                                str(random.randint(1, 1)),
                            ]
                        ]

                elif pyxel.tilemaps[0].pget(tile_x, tile_y) == (1, 2):
                    for i in range(
                        random.choice(
                            [
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                1,
                            ]
                        )
                    ):
                        tmp = random.randint(1, 3)
                        if tmp == 1:
                            self.props[tile_y * 8 + random.randint(1, 7)] += [
                                [
                                    "snow_tree",
                                    tile_x * 8 + random.randint(1, 7),
                                    str(random.randint(1, 3)),
                                ]
                            ]
                        elif tmp == 2:
                            self.props[tile_y * 8 + random.randint(1, 7)] += [
                                [
                                    "snow_bush",
                                    tile_x * 8 + random.randint(1, 7),
                                    str(random.randint(1, 4)),
                                ]
                            ]
                        else:
                            self.props[tile_y * 8 + random.randint(1, 7)] += [
                                [
                                    "snow_rock",
                                    tile_x * 8 + random.randint(1, 7),
                                    str(random.randint(1, 4)),
                                ]
                            ]

        self.portal_spawnable_tile = []
        for y in range(239):
            for x in range(215):
                tile = pyxel.tilemaps[0].pget(x, y)
                for type_of_tile in self.tile_type:
                    if self.tile_id_collision[type_of_tile].count(tile) == 1:
                        if ["no_collision_terrain", "path", "ice"].count(
                            type_of_tile
                        ) == 1:
                            self.portal_spawnable_tile.append((x, y))
                        break

        self.spirit_particles = []

        # Spirit world
        self.spirit_nodes = []
        self.monsters = []
        self.projectiles = []
        self.particles = []  # pour effets d’impact visibles
        self.memory_fragments = []
        self.save = {}

        # Ritual
        self.ritual_active = False
        self.ritual_progress = 0

        pyxel.run(self.update, self.draw)

    def load_save(self):
        for key in self.save:
            if key == "hud":
                self.hud = self.save[key]
            elif key == "player":
                self.player = self.save[key]
            elif key == "state":
                self.state = self.save[key]
            elif key == "portals":
                self.portals = self.save[key]
            elif key == "monsters":
                self.monsters = self.save[key]

    def save_game(self):
        self.save = {
            "hud": None,
            "player": {
                "x": self.player["x"],
                "y": self.player["y"],
                "x_spirit": self.player["x_spirit"],
                "y_spirit": self.player["y_spirit"],
                "vx": 0,
                "vy": 0,
                "hp": self.player["hp"],
                "faith": self.player["faith"],
                "inventory": self.player["inventory"],
                "active_slots": self.player["active_slots"],
                "anim": 0,  # animation frame
                "portal_id": self.player["portal_id"],
                "immortality": False,
                "immortality_start_frame": 0,
                "cooldown": False,
                "cooldown_start_frame": 0,
                "active_attack": self.player["active_attack"],
                "slot_at_mouse": [None, None],  # [ui_of_slot, slot_id]
                "selected_slot": [None, None],  # [ui_of_slot, slot_id]
            },
            "state": self.state,
            "portals": self.portals,
            "monsters": self.monsters,
        }

    # ============================================================
    # UPDATE
    # ============================================================

    def update(self):
        if self.ingame_hud.count(self.hud) == 1:
            self.update_player()

            if self.state == STATE_REAL:
                if (pyxel.frame_count - self.state_entry_frame) % 228 == 0:
                    pyxel.play(1, 2)
                self.update_real()
            elif self.state == STATE_SPIRIT_SUB_ZONE:
                if (pyxel.frame_count - self.state_entry_frame) % 195 == 0:
                    pyxel.play(1, 12)
                self.update_spirit_sub_zone()
            else:
                if (pyxel.frame_count - self.state_entry_frame) % 228 == 0:
                    pyxel.play(1, 0)
                self.update_spirit()

        else:
            if (pyxel.frame_count - self.state_entry_frame) % 255 == 0:
                pyxel.play(1, 4)
            self.update_outofgame_ui()

    def update_player(self):
        move = (
            (pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT))
            - (pyxel.btn(pyxel.KEY_Q) or pyxel.btn(pyxel.KEY_LEFT)),
            (pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN))
            - (pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.KEY_UP)),
        )

        if self.state != STATE_SPIRIT_SUB_ZONE:
            player_x = self.player["x"]
            player_y = self.player["y"]
        else:
            player_x = self.player["x_spirit"]
            player_y = self.player["y_spirit"]

        # temporary if statement for something that I didn't write yet
        if self.state != STATE_SPIRIT_SUB_ZONE:
            tile_of_player = pyxel.tilemaps[0].pget(
                (player_x + move[0] * 2) // 8 + 16, (player_y + move[1] * 2) // 8 + 16
            )
            for type_of_tile in self.tile_type:
                if self.tile_id_collision[type_of_tile].count(tile_of_player) == 1:
                    if self.tile_type[type_of_tile] != None:
                        if (
                            self.tile_type[type_of_tile].count(
                                pyxel.image(0).pget(
                                    tile_of_player[0] * 8
                                    + (player_x + move[0] * 2) % 8
                                    + move[0] * 1,
                                    tile_of_player[1] * 8
                                    + (player_y + move[1] * 2) % 8
                                    + move[1] * 1,
                                )
                            )
                            == 1
                        ):
                            move = (0, 0)
        else:
            tile_of_player = pyxel.tilemaps[2].pget(
                (player_x + move[0] * 2) // 8 + 16, (player_y + move[1] * 2) // 8 + 16
            )
            for type_of_tile in self.tile_type_spirit_sub:
                if (
                    self.tile_id_collision_spirit_sub[type_of_tile].count(
                        tile_of_player
                    )
                    == 1
                ):
                    if self.tile_type_spirit_sub[type_of_tile] != None:
                        if (
                            self.tile_type_spirit_sub[type_of_tile].count(
                                pyxel.image(1).pget(
                                    tile_of_player[0] * 8
                                    + (player_x + move[0] * 2) % 8
                                    + move[0] * 1,
                                    tile_of_player[1] * 8
                                    + (player_y + move[1] * 2) % 8
                                    + move[1] * 1,
                                )
                            )
                            == 1
                        ):
                            move = (0, 0)

        if self.state == STATE_SPIRIT:
            if (
                math.sqrt(
                    (
                        (self.player["x"] + move[0] * 2)
                        - self.portals[self.player["portal_id"]]["x"]
                    )
                    ** 2
                    + (
                        (self.player["y"] + move[1] * 2)
                        - self.portals[self.player["portal_id"]]["y"]
                    )
                    ** 2
                )
                > 139
            ):
                move = (0, 0)

        self.player["vx"] = move[0] * 1
        self.player["vy"] = move[1] * 1

        if self.state != STATE_SPIRIT_SUB_ZONE:
            #                                      v : taille de la map
            self.player["x"] = max(-WIDTH // 2, min(1596, player_x + self.player["vx"]))
            self.player["y"] = max(
                -HEIGHT // 2, min(1916, player_y + self.player["vy"])
            )
        else:
            #                                      v : taille de la map
            self.player["x_spirit"] = max(
                -WIDTH // 2, min(1596, player_x + self.player["vx"])
            )
            self.player["y_spirit"] = max(
                -HEIGHT // 2, min(1916, player_y + self.player["vy"])
            )

        if (
            self.player["immortality"] == True
            and pyxel.frame_count - self.player["immortality_start_frame"] > 15
        ):
            self.player["immortality"] = False

        if (
            self.player["cooldown"] == True
            and pyxel.frame_count - self.player["cooldown_start_frame"] > 6
        ):
            self.player["cooldown"] = False
        else:  # UPDATE UI --------------------------------------------------------------
            if pyxel.mouse_wheel != 0 and self.state != STATE_REAL:
                self.player["active_attack"] = self.player["active_slots"][
                    (
                        self.player["active_slots"].index(self.player["active_attack"])
                        + pyxel.mouse_wheel
                    )
                    % 3
                ]

        if self.player["hp"] <= 0:
            self.hud = "dead"

        if pyxel.btnp(pyxel.KEY_E, 15, 1):
            if self.hud == None:
                self.hud = "inventory"
            else:
                self.hud = None
                self.player["slot_at_mouse"] = [None, None]
                self.player["selected_slot"] = [None, None]

        if pyxel.btnp(pyxel.KEY_ESCAPE, 15, 1):
            if self.hud == None:
                self.hud = "pause"
                self.state_entry_frame = pyxel.frame_count + 1
            else:
                self.hud = None
                self.player["slot_at_mouse"] = [None, None]
                self.player["selected_slot"] = [None, None]

        if self.hud == "inventory":
            self.player["slot_at_mouse"] = [None, None]

            for i in range(len(self.player["inventory"])):
                if (
                    pyxel.mouse_x > 77 + (i % 4) * 19
                    and pyxel.mouse_x < 94 + (i % 4) * 19
                    and pyxel.mouse_y > 147 + (i // 4) * 19
                    and pyxel.mouse_y < 164 + (i // 4) * 19
                ):
                    self.player["slot_at_mouse"] = ["inventory", i]
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, 15, 1):
                        if self.player["selected_slot"] == [None, None]:
                            self.player["selected_slot"] = ["inventory", i]
                        else:
                            selected_slot_id, selected_slot_in = (
                                self.player["selected_slot"][1],
                                self.player["selected_slot"][0],
                            )
                            slot_at_mouse_id, slot_at_mouse_in = (
                                self.player["slot_at_mouse"][1],
                                self.player["slot_at_mouse"][0],
                            )
                            (
                                self.player[selected_slot_in][selected_slot_id],
                                self.player[slot_at_mouse_in][slot_at_mouse_id],
                            ) = (
                                self.player[slot_at_mouse_in][slot_at_mouse_id],
                                self.player[selected_slot_in][selected_slot_id],
                            )
                            self.player["selected_slot"] = [None, None]
                            if (
                                self.player["active_slots"].count(
                                    self.player["active_attack"]
                                )
                                == 0
                            ):
                                if self.player["active_slots"].count(None) == 0:
                                    self.player["active_attack"] = self.player[
                                        "active_slots"
                                    ][0]
                                else:
                                    self.player["active_attack"] = None
                    break

            for i in range(3):
                if (
                    pyxel.mouse_x > 159
                    and pyxel.mouse_x < 177
                    and pyxel.mouse_y > 147 + i * 19
                    and pyxel.mouse_y < 164 + i * 19
                ):
                    self.player["slot_at_mouse"] = ["active_slots", i]
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, 15, 1):
                        if self.player["selected_slot"] == [None, None]:
                            self.player["selected_slot"] = ["active_slots", i]
                        else:
                            selected_slot_id, selected_slot_in = (
                                self.player["selected_slot"][1],
                                self.player["selected_slot"][0],
                            )
                            slot_at_mouse_id, slot_at_mouse_in = (
                                self.player["slot_at_mouse"][1],
                                self.player["slot_at_mouse"][0],
                            )
                            (
                                self.player[selected_slot_in][selected_slot_id],
                                self.player[slot_at_mouse_in][slot_at_mouse_id],
                            ) = (
                                self.player[slot_at_mouse_in][slot_at_mouse_id],
                                self.player[selected_slot_in][selected_slot_id],
                            )
                            self.player["selected_slot"] = [None, None]
                            if (
                                self.player["active_slots"].count(
                                    self.player["active_attack"]
                                )
                                == 0
                            ):
                                if self.player["active_slots"].count(None) == 0:
                                    self.player["active_attack"] = self.player[
                                        "active_slots"
                                    ][0]
                                else:
                                    self.player["active_attack"] = None
                    break

        self.qol_loot_ui = [
            l
            for l in self.qol_loot_ui
            if pyxel.frame_count - l["obtention_frame"] < 150
        ]

        # animation du joueur
        if move != (0, 0):
            if pyxel.frame_count % 10 == 0:
                pyxel.play(2, 6)
                self.player["anim"] = 1 - self.player["anim"]

    def update_outofgame_ui(self):
        self.player["selected_slot"] = [None, None]
        self.player["slot_at_mouse"] = [None, None]
        if pyxel.btnp(pyxel.KEY_ESCAPE, 15, 1):
            self.hud = None
            self.state_entry_frame = pyxel.frame_count + 1
        if self.hud == "pause":
            for i in range(len(self.pause_ui_text_id)):
                if (
                    pyxel.mouse_x > 8
                    and pyxel.mouse_x < 12 + self.pause_ui_text_id[i][2]
                    and pyxel.mouse_y > 18 + i * 30
                    and pyxel.mouse_y < 30 + i * 30
                ):
                    self.player["slot_at_mouse"] = ["pause", i]
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, 15, 1):
                        if i == 0:
                            self.state_entry_frame = pyxel.frame_count + 1
                            self.hud = None
                            self.player["selected_slot"] = [None, None]
                            self.player["slot_at_mouse"] = [None, None]
                        elif i == 2:
                            self.save_game()
                            pyxel.quit()
                        elif i == 3:
                            self.save_game()
                        else:
                            self.player["selected_slot"] = ["pause", i]
                    break

            if self.player["selected_slot"] != [None, None]:
                self.hud = self.pause_sub_hud[self.player["selected_slot"][1]]
                self.player["slot_at_mouse"] = [None, None]

        elif self.hud == "quit_warning":
            for i in range(2):
                if (
                    pyxel.mouse_x > 93 + i * 48
                    and pyxel.mouse_x < 115 + i * 48
                    and pyxel.mouse_y > 131
                    and pyxel.mouse_y < 145
                ):
                    self.player["slot_at_mouse"] = ["quit_warning", i]
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, 15, 1):
                        if i == 0:
                            pyxel.quit()
                        else:
                            self.hud = "pause"
                            self.player["selected_slot"] = [None, None]
                            self.player["slot_at_mouse"] = [None, None]
                    break

        elif self.hud == "dead":
            for i in range(2):
                if (
                    pyxel.mouse_x > 62 + i * 100
                    and pyxel.mouse_x < 94 + i * 100
                    and pyxel.mouse_y > 170
                    and pyxel.mouse_y < 186
                ):
                    self.player["slot_at_mouse"] = ["dead", i]
                    if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT, 15, 1):
                        if i == 1:
                            pyxel.quit()
                        else:
                            self.hud = None
                            self.load_save()

                    break

    # ============================================================
    # Monster pathfinding
    # ============================================================

    def init_path_map(self):

        portal = self.portals[self.player["portal_id"]]
        self.path_map = []

        for y in range(300 // 8):
            self.path_map += [[]]
            for x in range(300 // 8):
                if math.sqrt((x - 150 // 8) ** 2 + (y - 150 // 8) ** 2) > 19:
                    self.path_map[y].append(1)
                else:
                    tile = pyxel.tilemaps[0].pget(
                        (portal["x"] - 150) // 8 + x + 17,
                        (portal["y"] - 150) // 8 + y + 17,
                    )

                    for type_of_tile in self.tile_type:
                        if self.tile_id_collision[type_of_tile].count(tile) == 1:
                            if [
                                "no_collision_terrain",
                                "ice",
                                "path",
                                "brick_bridge",
                                "wood_bridge",
                            ].count(type_of_tile) == 1:
                                self.path_map[y].append(0)
                            else:
                                self.path_map[y].append(1)
                            break

        # print(self.path_map)

    def init_path_map_spirit_sub_mine(self):

        mine = self.mine_path[self.portals[self.player["portal_id"]]["id"]]
        self.path_map = []
        for y in range(mine["h"] // 8):
            self.path_map += [[]]
            for x in range(mine["l"] // 8):
                tile = pyxel.tilemaps[2].pget(mine["x"] // 8 + x, mine["y"] // 8 + y)
                for type_of_tile in self.tile_type_spirit_sub:
                    if self.tile_id_collision_spirit_sub[type_of_tile].count(tile) == 1:
                        if type_of_tile != "terrain":
                            self.path_map[y].append(0)
                        else:
                            self.path_map[y].append(1)
                        break

    def monster_pathfinding(self, monster):
        path_map = self.path_map.copy()
        start = (monster["x"] // 8 + 16, monster["y"] // 8 + 16)
        end = (self.player["x"] // 8 + 16, self.player["y"] // 8 + 16)

        portal = self.portals[self.player["portal_id"]]
        if portal["type"] == "portal":
            u, v = portal["x"] // 8 + 16 - 150 // 8, portal["y"] // 8 + 16 - 150 // 8
        elif portal["type"] == "mine":
            mine = self.mine_path[portal["id"]]
            u, v = mine["x"] // 8 - 16, mine["y"] // 8 - 16
            start = (monster["x"] // 8, monster["y"] // 8)
            end = (self.player["x_spirit"] // 8, self.player["y_spirit"] // 8)

        width = len(path_map[0])
        height = len(path_map)

        # Conversion monde -> local
        def to_local(pos):
            return (pos[0] - u, pos[1] - v)

        def in_bounds(x, y):
            return 0 <= x < width and 0 <= y < height

        def is_walkable(x, y):
            return path_map[int(y)][int(x)] == 0

        start_l = to_local(start)
        end_l = to_local(end)

        if not is_walkable(end_l[0], end_l[1]):
            path_map[end_l[1]][end_l[0]] = 0

        open_list = [start_l]
        closed_set = set()

        came_from = {}
        g_score = {start_l: 0}
        f_score = {start_l: self.heuristic_dist(start_l, end_l)}

        directions = [
            (-1, 0, 1),
            (1, 0, 1),
            (0, -1, 1),
            (0, 1, 1),
            (-1, -1, math.sqrt(2)),
            (1, -1, math.sqrt(2)),
            (-1, 1, math.sqrt(2)),
            (1, 1, math.sqrt(2)),
        ]

        while open_list:
            current = min(open_list, key=lambda n: f_score[n])

            if current == end_l:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_l)
                path.reverse()
                return path  # coordonnées LOCALES

            open_list.remove(current)
            closed_set.add(current)

            x, y = current

            for dx, dy, cost in directions:
                nx, ny = x + dx, y + dy
                neighbor = (nx, ny)

                if not in_bounds(nx, ny):
                    continue
                if not is_walkable(nx, ny):
                    continue
                if neighbor in closed_set:
                    continue

                # Anti corner-cutting
                if dx != 0 and dy != 0:
                    if not (is_walkable(x + dx, y) and is_walkable(x, y + dy)):
                        continue

                tentative_g = g_score[current] + cost

                if neighbor not in open_list:
                    open_list.append(neighbor)
                elif tentative_g >= g_score.get(neighbor, float("inf")):
                    continue

                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + self.heuristic_dist(neighbor, end_l)

        return None

    # ============================================================
    # REAL WORLD
    # ============================================================

    def update_real(self):
        if pyxel.frame_count % 1800 == 0:
            self.portals = [p for p in self.portals if p["type"] != "portal"]
            for i in range(30):
                tile = random.choice(self.portal_spawnable_tile)
                self.portals.append(
                    {
                        "x": tile[0] * 8 - 120,
                        "y": tile[1] * 8 - 120,
                        "purified": False,
                        "type": "portal",
                        "start_time": 0,
                        "state": STATE_SPIRIT,
                    }
                )

        if pyxel.frame_count % 90 == 0:
            # Gain de foi progressive
            if self.player["faith"] <= 100:
                self.player["faith"] += 1
            # Gain de vie progressive
            if self.player["hp"] < 98:
                self.player["hp"] += 3
            elif self.player["hp"] < 100:
                self.player["hp"] = 100

        near_portal = None

        for p in self.portals:
            x_clip, y_clip = 0, 0
            if p["type"] == "mine":
                x_clip, y_clip = 9, 9
            if (
                not p["purified"]
                and self.dist(self.player, {"x": p["x"] + x_clip, "y": p["y"] + y_clip})
                < 10
            ):
                near_portal = p

        # Rituel
        if near_portal:
            if pyxel.btn(pyxel.KEY_SPACE):
                self.ritual_active = True
                self.ritual_progress += 1

                if self.ritual_progress % 12 == 0:
                    self.player["faith"] -= 1

                if self.ritual_progress >= 60:
                    self.player["portal_id"] = self.portals.index(near_portal)
                    self.state = near_portal["state"]
                    if self.state == STATE_SPIRIT:
                        self.enter_spirit()
                    else:
                        self.enter_spirit_sub_zone()
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

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.player["cooldown"] == False:
            if self.player["active_attack"] != None:
                if self.attack_ui[self.player["active_attack"]]["type"] == "ranged":
                    self.player["cooldown"] = True
                    self.player["cooldown_start_frame"] = pyxel.frame_count
                    dif_x = (128) - pyxel.mouse_x
                    dif_y = (128) - pyxel.mouse_y
                    # défaut : tir vers la droite
                    if dif_x == 0 and dif_y == 0:
                        dx = 1
                        dy = 0
                    elif dif_x == 0:
                        dx = 0
                        dy = -dif_y / abs(dif_y)
                    elif dif_y == 0:
                        dx = -dif_x / abs(dif_x)
                        dy = 0
                    elif abs(dif_x) > abs(dif_y):
                        dx = -dif_x / abs(dif_x)
                        dy = -dif_y / abs(dif_x)
                    else:
                        dx = -dif_x / abs(dif_y)
                        dy = -dif_y / abs(dif_y)

                    self.projectiles.append(
                        {
                            "x": self.player["x"],
                            "y": self.player["y"],
                            "dx": dx,
                            "dy": dy,
                            "spd": 3,
                            "life": 40,
                            "type": self.player["active_attack"],
                        }
                    )

                elif self.attack_ui[self.player["active_attack"]]["type"] == "closed":
                    pyxel.play(3, 5)
                    self.player["cooldown_start_frame"] = pyxel.frame_count
                    for m in self.monsters:
                        if 128 > pyxel.mouse_x:
                            clipping = -16
                        else:
                            clipping = 0
                        tmp = {
                            "x": self.player["x"] + 14 + clipping * 1.625,
                            "y": self.player["y"],
                        }

                        if self.dist(tmp, m, "x", "y") < 12:
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
        for i in range(len(self.monsters)):
            m = self.monsters[i]
            if not m["stun"]:
                # contact joueur
                if self.dist(self.player, m, "x", "y") < 6:
                    if self.player["immortality"] == False:
                        if self.player["hp"] > 0:
                            self.player["hp"] -= 10
                        self.player["immortality"] = True
                        self.player["immortality_start_frame"] = pyxel.frame_count
                else:
                    path = self.monster_pathfinding(m)
                    portal = self.portals[self.player["portal_id"]]
                    u, v = portal["x"] // 8 - 2, portal["y"] // 8 - 2
                    if i == 0:
                        self.temp = path
                    if path != None:
                        if len(path) > 1:
                            path = path[1:]
                            m["vx"] = ((path[0][0] + u) - (m["x"] // 8 + 16)) * m["spd"]
                            m["vy"] = ((path[0][1] + v) - (m["y"] // 8 + 16)) * m["spd"]
                            m["x"] += m["vx"]
                            m["y"] += m["vy"]
                        else:
                            m["vx"] = (
                                1
                                if self.player["x"] > m["x"]
                                else -1 if self.player["x"] < m["x"] else 0
                            )
                            m["vy"] = (
                                1
                                if self.player["y"] > m["y"]
                                else -1 if self.player["y"] < m["y"] else 0
                            )
                            m["x"] += m["vx"] * m["spd"]
                            m["y"] += m["vy"] * m["spd"]

                        m["anim"] = (pyxel.frame_count // 10) % 2
                    else:
                        if (
                            self.portals[self.player["portal_id"]]["start_time"]
                            == pyxel.frame_count
                        ):
                            self.monsters = self.monsters[:i] + self.monsters[i:]

        # -------------------------------
        # COLLISIONS projectile → monstre
        # -------------------------------
        for p in self.projectiles:
            for m in self.monsters:
                if self.dist(p, m) < 6:
                    if p["type"] == "poison_bomb":
                        m["hp"] -= 1
                        self.projectile_info_impact.append(
                            {
                                "x": p["x"],
                                "y": p["y"],
                                "impact_frame": pyxel.frame_count,
                                "type": "poison_bomb",
                            }
                        )
                    elif p["type"] == "cryogenis":
                        m["hp"] -= 0.1
                        temp = False
                        for p2 in self.projectile_info_impact:
                            if self.dist(p, p2) < 6:
                                temp = True
                                p2["impact_frame"] = pyxel.frame_count
                                break
                        if not temp:
                            self.projectile_info_impact.append(
                                {
                                    "x": p["x"],
                                    "y": p["y"],
                                    "impact_frame": pyxel.frame_count,
                                    "type": "cryogenis",
                                }
                            )
                    else:
                        m["hp"] -= 1
                    p["life"] = 0
                    self.spawn_hit_particles(m["x"], m["y"])

        for p in self.projectile_info_impact:
            for m in self.monsters:

                if p["type"] == "poison_bomb":
                    if self.dist(p, m) < 10:
                        m["hp"] -= 0.01
                elif p["type"] == "cryogenis":
                    if self.dist(p, m) < 6:
                        if (
                            pyxel.frame_count - p["impact_frame"]
                            < self.attack_ui[p["type"]]["damage_frame"] - 1
                        ):
                            m["stun"] = True
                        else:
                            m["stun"] = False
                        # self.spawn_hit_particles(m["x"], m["y"])

        # nettoyer
        regen_faith_wkill = len(self.monsters)
        self.projectile_info_impact = [
            p
            for p in self.projectile_info_impact
            if pyxel.frame_count - p["impact_frame"]
            < self.attack_ui[p["type"]]["damage_frame"]
        ]
        self.projectiles = [p for p in self.projectiles if p["life"] > 0]
        self.monsters = [m for m in self.monsters if m["hp"] > 0]

        # régénération d'un peu de faith en tuant un monstre + loot
        if len(self.monsters) < regen_faith_wkill:
            monster_killed_at_frame = regen_faith_wkill - len(self.monsters)
            self.player["faith"] += monster_killed_at_frame * 5
            for i in range(monster_killed_at_frame):
                if self.player["inventory"].count(None) > 0:
                    rd = random.randint(0, 100)
                    if rd > 97:
                        self.player["inventory"][
                            self.player["inventory"].index(None)
                        ] = "poison_bomb"
                        self.qol_loot_ui.append(
                            {
                                "type": "poison_bomb",
                                "obtention_frame": pyxel.frame_count,
                            }
                        )
                    elif rd > 94:
                        self.player["inventory"][
                            self.player["inventory"].index(None)
                        ] = "cryogenis"
                        self.qol_loot_ui.append(
                            {"type": "cryogenis", "obtention_frame": pyxel.frame_count}
                        )
                    elif rd > 90:
                        self.player["inventory"][
                            self.player["inventory"].index(None)
                        ] = "sword"
                        self.qol_loot_ui.append(
                            {"type": "sword", "obtention_frame": pyxel.frame_count}
                        )
            if self.player["faith"] > 100:
                self.player["faith"] = 100

        # -------------------------------
        # PURIFICATION DES NŒUDS SPIRITUELS
        # -------------------------------
        for n in self.spirit_nodes:
            if not n["purified"] and self.dist(self.player, n, "x", "y") < 8:
                if pyxel.btnp(pyxel.KEY_SPACE):
                    n["purified"] = True
                    self.spawn_hit_particles(n["x"], n["y"])

        # tout purifié ?
        if len(self.monsters) == 0:
            self.exit_spirit(failed=False)
            self.portals = (
                self.portals[: self.player["portal_id"]]
                + self.portals[(self.player["portal_id"] + 1) :]
            )

        # update des particules
        for h in self.particles:
            h["x"] += h["dx"]
            h["y"] += h["dy"]
            h["life"] -= 1

        if pyxel.frame_count % 4 == 0:
            for i in range(200):
                particle = (
                    self.portals[self.player["portal_id"]]["x"] + math.cos(i / 8) * 150,
                    self.portals[self.player["portal_id"]]["y"]
                    + math.sin(i / 8) * 150
                    + random.randint(0, 3)
                    - 15,
                )

                tile_of_particle = pyxel.tilemaps[0].pget(
                    particle[0] // 8 + 16, particle[1] // 8 + 16
                )
                for type_of_tile in self.tile_type:
                    if (
                        self.tile_id_collision[type_of_tile].count(tile_of_particle)
                        == 1
                    ):
                        if ["water", "terrain", "forest"].count(type_of_tile) == 0:
                            self.spawn_spirit_particles(
                                particle[0], particle[1], random.randint(5, 8)
                            )
                        break

            # print(self.spirit_particles)
            for t in self.spirit_particles:
                t["y"] += 1
                t["life"] -= 1

            self.spirit_particles = [t for t in self.spirit_particles if t["life"] > 0]

        # print(self.spirit_particles)
        # print(self.particles)

        self.particles = [h for h in self.particles if h["life"] > 0]

    def update_spirit_sub_zone(self):
        near_portal = None
        portal = self.portals[self.player["portal_id"]]

        if portal["type"] == "mine":
            for p in self.mine_exit:
                if (
                    self.dist(
                        self.player,
                        {"x": p["x"] + 9, "y": p["y"] + 9},
                        "x_spirit",
                        "y_spirit",
                    )
                    < 10
                ):
                    near_portal = p

            # Rituel
            if near_portal:
                if pyxel.btn(pyxel.KEY_SPACE):
                    self.ritual_active = True
                    self.ritual_progress += 1

                    if self.ritual_progress >= 60:
                        self.player["portal_id"] = None
                        self.player["x"], self.player["y"] = (
                            near_portal["x_real"] + 9,
                            near_portal["y_real"] + 12,
                        )
                        self.exit_spirit(failed=False)
                        self.ritual_active = False
                        self.ritual_progress = 0
                else:
                    # si SPACE relâché, reset
                    if self.ritual_active:
                        self.ritual_active = False
                        self.ritual_progress = 0

        # Perte de foi progressive
        if pyxel.frame_count % 30 == 0:
            self.player["faith"] -= 1
            if self.player["faith"] <= 0:
                self.exit_spirit(failed=True)

        # -------------------------------
        # ATTAQUE (LEFT CLICK)
        # -------------------------------
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and self.player["cooldown"] == False:
            if self.player["active_attack"] != None:
                if self.attack_ui[self.player["active_attack"]]["type"] == "ranged":
                    self.player["cooldown"] = True
                    self.player["cooldown_start_frame"] = pyxel.frame_count
                    dif_x = 128 - pyxel.mouse_x
                    dif_y = 128 - pyxel.mouse_y
                    # défaut : tir vers la droite
                    if dif_x == 0 and dif_y == 0:
                        dx = 1
                        dy = 0
                    elif dif_x == 0:
                        dx = 0
                        dy = -dif_y / abs(dif_y)
                    elif dif_y == 0:
                        dx = -dif_x / abs(dif_x)
                        dy = 0
                    elif abs(dif_x) > abs(dif_y):
                        dx = -dif_x / abs(dif_x)
                        dy = -dif_y / abs(dif_x)
                    else:
                        dx = -dif_x / abs(dif_y)
                        dy = -dif_y / abs(dif_y)

                    self.projectiles.append(
                        {
                            "x": self.player["x_spirit"],
                            "y": self.player["y_spirit"],
                            "dx": dx,
                            "dy": dy,
                            "spd": 3,
                            "life": 40,
                            "type": self.player["active_attack"],
                        }
                    )

                elif self.attack_ui[self.player["active_attack"]]["type"] == "closed":
                    self.player["cooldown_start_frame"] = pyxel.frame_count
                    for m in self.monsters:
                        if 128 > pyxel.mouse_x:
                            clipping = -16
                        else:
                            clipping = 0
                        tmp = {
                            "x_spirit": self.player["x_spirit"] + 14 + clipping * 1.625,
                            "y_spirit": self.player["y_spirit"],
                        }

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

        for i in range(len(self.monsters)):
            m = self.monsters[i]
            if not m["stun"]:
                # contact joueur
                if self.dist(self.player, m, "x_spirit", "y_spirit") < 6:
                    if self.player["immortality"] == False:
                        if self.player["hp"] > 0:
                            self.player["hp"] -= 10
                        self.player["immortality"] = True
                        self.player["immortality_start_frame"] = pyxel.frame_count
                else:
                    path = self.monster_pathfinding(m)
                    mine = self.mine_path[portal["id"]]
                    u, v = mine["x"] // 8 - 16, mine["y"] // 8 - 16
                    if i == 0:
                        self.temp = path
                    if path != None:
                        if len(path) > 1:
                            path = path[1:]
                            m["vx"] = ((path[0][0] + u) - (m["x"] // 8)) * m["spd"]
                            m["vy"] = ((path[0][1] + v) - (m["y"] // 8)) * m["spd"]
                            m["x"] += m["vx"]
                            m["y"] += m["vy"]
                        else:
                            m["vx"] = (
                                1
                                if self.player["x_spirit"] > m["x"]
                                else -1 if self.player["x_spirit"] < m["x"] else 0
                            )
                            m["vy"] = (
                                1
                                if self.player["y_spirit"] > m["y"]
                                else -1 if self.player["y_spirit"] < m["y"] else 0
                            )
                            m["x"] += m["vx"] * m["spd"]
                            m["y"] += m["vy"] * m["spd"]

                        m["anim"] = (pyxel.frame_count // 10) % 2
                    else:
                        if (
                            self.portals[self.player["portal_id"]]["start_time"]
                            == pyxel.frame_count
                        ):
                            self.monsters = self.monsters[:i] + self.monsters[i:]

        # -------------------------------
        # COLLISIONS projectile → monstre
        # -------------------------------
        for p in self.projectiles:
            for m in self.monsters:
                if self.dist(p, m) < 6:
                    if p["type"] == "poison_bomb":
                        m["hp"] -= 1
                        self.projectile_info_impact.append(
                            {
                                "x": p["x"],
                                "y": p["y"],
                                "impact_frame": pyxel.frame_count,
                                "type": "poison_bomb",
                            }
                        )
                    elif p["type"] == "cryogenis":
                        m["hp"] -= 0.1
                        temp = False
                        for p2 in self.projectile_info_impact:
                            if self.dist(p, p2) < 6:
                                temp = True
                                p2["impact_frame"] = pyxel.frame_count
                                break
                        if not temp:
                            self.projectile_info_impact.append(
                                {
                                    "x": p["x"],
                                    "y": p["y"],
                                    "impact_frame": pyxel.frame_count,
                                    "type": "cryogenis",
                                }
                            )
                    else:
                        m["hp"] -= 1
                    p["life"] = 0
                    self.spawn_hit_particles(m["x"], m["y"])

        for p in self.projectile_info_impact:
            for m in self.monsters:
                if p["type"] == "poison_bomb":
                    if self.dist(p, m) < 10:
                        m["hp"] -= 0.01
                elif p["type"] == "cryogenis":
                    if self.dist(p, m) < 6:
                        if (
                            pyxel.frame_count - p["impact_frame"]
                            < self.attack_ui[p["type"]]["damage_frame"] - 1
                        ):
                            m["stun"] = True
                        else:
                            m["stun"] = False
                        # self.spawn_hit_particles(m["x"], m["y"])

        # nettoyer
        regen_faith_wkill = len(self.monsters)
        self.projectile_info_impact = [
            p
            for p in self.projectile_info_impact
            if pyxel.frame_count - p["impact_frame"]
            < self.attack_ui[p["type"]]["damage_frame"]
        ]
        self.projectiles = [p for p in self.projectiles if p["life"] > 0]
        self.monsters = [m for m in self.monsters if m["hp"] > 0]

        # régénération d'un peu de faith en tuant un monstre + loot
        if len(self.monsters) < regen_faith_wkill:
            monster_killed_at_frame = regen_faith_wkill - len(self.monsters)
            self.player["faith"] += monster_killed_at_frame * 5
            for i in range(monster_killed_at_frame):
                if self.player["inventory"].count(None) > 0:
                    rd = random.randint(0, 100)
                    if rd > 97:
                        self.player["inventory"][
                            self.player["inventory"].index(None)
                        ] = "poison_bomb"
                        self.qol_loot_ui.append(
                            {
                                "type": "poison_bomb",
                                "obtention_frame": pyxel.frame_count,
                            }
                        )
                    elif rd > 94:
                        self.player["inventory"][
                            self.player["inventory"].index(None)
                        ] = "cryogenis"
                        self.qol_loot_ui.append(
                            {"type": "cryogenis", "obtention_frame": pyxel.frame_count}
                        )
                    elif rd > 90:
                        self.player["inventory"][
                            self.player["inventory"].index(None)
                        ] = "sword"
                        self.qol_loot_ui.append(
                            {"type": "sword", "obtention_frame": pyxel.frame_count}
                        )
            if self.player["faith"] > 100:
                self.player["faith"] = 100

        # -------------------------------
        # PURIFICATION DES NŒUDS SPIRITUELS
        # -------------------------------
        for n in self.spirit_nodes:
            if (
                not n["purified"]
                and self.dist(self.player, n, "x_spirit", "y_spirit") < 8
            ):
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
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "dx": math.cos(angle) * speed,
                    "dy": math.sin(angle) * speed,
                    "life": random.randint(10, 20),
                }
            )

    def spawn_spirit_particles(self, x, y, height):
        if pyxel.frame_count % 5 == 0:
            h = random.randint(1, 3)
            self.spirit_particles.append(
                {
                    "x": x,
                    "y": y,
                    "h": h,
                    "life": height + 2 * h,
                    "col": random.choice([1, 5, 6, 12]),  # random.choice([2, 4, 8, 14])
                }
            )

    # ============================================================
    # EVENTS
    # ============================================================

    def enter_spirit(self):
        self.state_entry_frame = pyxel.frame_count + 1
        self.ritual_active = False
        self.ritual_progress = 0
        self.monsters = []
        self.player["immortality"] = True
        portal = self.portals[self.player["portal_id"]]
        self.portals[self.player["portal_id"]]["start_time"] = pyxel.frame_count
        spawnable_tile_list = []
        if self.state != STATE_SPIRIT_SUB_ZONE:
            self.init_path_map()

        for tile_y in range(300):
            for tile_x in range(round(math.sin(tile_y / 300 * math.pi) * 300)):
                if tile_y % 8 == 0 and tile_x % 8 == 0:
                    coo_right = (portal["x"] + tile_x, portal["y"] + tile_y - 150)
                    coo_left = (portal["x"] - tile_x, portal["y"] + tile_y - 150)
                    if self.dist(portal, {"x": coo_right[0], "y": coo_right[1]}) < 140:

                        tile_right = pyxel.tilemaps[0].pget(
                            coo_right[0] // 8 + 16, coo_right[1] // 8 + 16
                        )
                        tile_left = pyxel.tilemaps[0].pget(
                            coo_left[0] // 8 + 16, coo_left[1] // 8 + 16
                        )

                        for type_of_tile in self.tile_type:
                            if (
                                self.tile_id_collision[type_of_tile].count(tile_right)
                                == 1
                            ):
                                if ["no_collision_terrain", "path", "ice"].count(
                                    type_of_tile
                                ) == 1:
                                    if (
                                        math.sqrt(
                                            ((self.player["x"]) - coo_right[0]) ** 2
                                            + ((self.player["y"]) - coo_right[1]) ** 2
                                        )
                                        > 48
                                    ):
                                        spawnable_tile_list.append(coo_right)
                                break

                        for type_of_tile in self.tile_type:
                            if (
                                self.tile_id_collision[type_of_tile].count(tile_left)
                                == 1
                            ):
                                if ["no_collision_terrain", "path", "ice"].count(
                                    type_of_tile
                                ) == 1:
                                    if (
                                        math.sqrt(
                                            ((self.player["x"]) - coo_left[0]) ** 2
                                            + ((self.player["y"]) - coo_left[1]) ** 2
                                        )
                                        > 48
                                    ):
                                        spawnable_tile_list.append(coo_left)
                                break

        # Monstres animés
        for i in range(random.randint(3, 8)):
            monster_tile = random.choice(spawnable_tile_list)
            index = spawnable_tile_list.index(monster_tile)
            spawnable_tile_list = (
                spawnable_tile_list[:index] + spawnable_tile_list[index:]
            )
            self.monsters.append(
                {
                    "x": monster_tile[0],
                    "y": monster_tile[1],
                    "vx": 1,
                    "vy": 1,
                    "hp": 4,
                    "spd": 0.6,
                    "anim": 0,
                    "stun": False,
                    "stun_start_frame": 0,
                    "stun_type": None,
                }
            )

    def enter_spirit_sub_zone(self):
        portal = self.portals[self.player["portal_id"]]
        if portal["type"] == "mine":
            mine = self.mine_path[portal["id"]]
            for mine_exit in self.mine_exit:
                if (portal["x"], portal["y"]) == (
                    mine_exit["x_real"],
                    mine_exit["y_real"],
                ):
                    self.player["x_spirit"], self.player["y_spirit"] = (
                        mine_exit["x"] + 9,
                        mine_exit["y"] + 10,
                    )
        self.state_entry_frame = pyxel.frame_count + 1
        self.ritual_active = False
        self.ritual_progress = 0
        self.player["immortality"] = True
        self.init_path_map_spirit_sub_mine()

        # Noeuds à purifier
        self.spirit_nodes = [
            {"x": 30, "y": 30, "purified": False},
            {"x": 96, "y": 40, "purified": False},
        ]

        # Monstres animés
        self.monsters = []
        spawnable_tile_list = []

        for y in range(len(self.path_map)):
            for x in range(len(self.path_map[y])):
                if self.path_map[y][x] == 0:
                    spawnable_tile_list.append((x, y))

        for i in range(random.randint(3, 8)):
            monster_tile = random.choice(spawnable_tile_list)
            index = spawnable_tile_list.index(monster_tile)
            spawnable_tile_list = (
                spawnable_tile_list[:index] + spawnable_tile_list[index:]
            )
            self.monsters.append(
                {
                    "x": monster_tile[0] * 8,
                    "y": monster_tile[1] * 8,
                    "vx": 1,
                    "vy": 1,
                    "hp": 4,
                    "spd": 0.6,
                    "anim": 0,
                    "stun": False,
                    "stun_start_frame": 0,
                    "stun_type": None,
                }
            )

    def exit_spirit(self, failed):
        self.state_entry_frame = pyxel.frame_count + 1
        self.state = STATE_REAL
        self.path_map = []

        if not failed:
            # purifier un portail
            for p in self.portals:
                if not p["purified"]:
                    p["purified"] = True
                    self.memory_fragments.append(
                        random.choice(
                            [
                                "« Une fracture traverse encore le monde... »",
                                "Une ombre murmure : « Tu te souviens ? »",
                                "Une larme tombe dans la poussière.",
                                "Un ancien cri déchire ton esprit.",
                            ]
                        )
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

        elif self.state == STATE_SPIRIT:
            self.draw_spirit()
        else:
            self.draw_spirit_sub_zone()

        self.draw_ui()

    # -------------------------------

    def draw_props(self):

        clipping = 0
        if self.state != STATE_REAL:
            clipping = 128

        self.props[self.player["y"] + 124] += [["player", 124, 1]]

        for y in range(len(self.props)):
            for prop in self.props[y]:

                if prop[0] == "tree":
                    pyxel.blt(
                        prop[1] - self.player["x"] - 8,
                        y - self.player["y"] - 10,
                        0,
                        240,
                        self.tree_id[prop[2]] + clipping,
                        16,
                        16,
                        7,
                    )
                elif prop[0] == "bush":
                    pyxel.blt(
                        prop[1] - self.player["x"] - 8,
                        y - self.player["y"],
                        0,
                        self.bush_id[prop[2]],
                        112 + clipping,
                        8,
                        8,
                        7,
                    )
                elif prop[0] == "rock":
                    pyxel.blt(
                        prop[1] - self.player["x"] - 8,
                        y - self.player["y"],
                        0,
                        self.rock_id[prop[2]],
                        120 + clipping,
                        8,
                        8,
                        7,
                    )
                elif prop[0] == "snow_tree":
                    pyxel.blt(
                        prop[1] - self.player["x"] - 8,
                        y - self.player["y"] - 10,
                        0,
                        16,
                        self.snow_tree_id[prop[2]] + clipping,
                        16,
                        16,
                        11,
                    )
                elif prop[0] == "snow_bush":
                    pyxel.blt(
                        prop[1] - self.player["x"] - 8,
                        y - self.player["y"],
                        0,
                        32,
                        self.snow_bush_id[prop[2]] + clipping,
                        8,
                        8,
                        11,
                    )
                elif prop[0] == "snow_rock":
                    pyxel.blt(
                        prop[1] - self.player["x"] - 8,
                        y - self.player["y"],
                        0,
                        40,
                        self.snow_rock_id[prop[2]] + clipping,
                        8,
                        8,
                        11,
                    )
                elif prop[0] == "cactus":
                    pyxel.blt(
                        prop[1] - self.player["x"] - 8,
                        y - self.player["y"] - 10,
                        0,
                        240,
                        self.cactus_id[prop[2]] + clipping,
                        16,
                        16,
                        7,
                    )
                elif prop[0] == "mountain":
                    pyxel.blt(
                        prop[1] - self.player["x"] - 8,
                        y - self.player["y"] - 10,
                        2,
                        112,
                        0,
                        64,
                        32,
                        2,
                    )

                elif prop[0] == "player":
                    if (self.player["vx"], self.player["vy"]) != (0, 0):
                        pyxel.blt(
                            prop[1],
                            y - self.player["y"],
                            0,
                            8 + 8 * self.player["vx"],
                            80
                            + 24 * self.player["vy"]
                            + ((pyxel.frame_count % 15) // 5) * 8,
                            8,
                            8,
                            7,
                        )
                    else:
                        pyxel.blt(prop[1], y - self.player["y"], 0, 8, 104, 8, 8, 7)
        self.props[self.player["y"] + 124].pop()

    # -------------------------------

    def draw_real(self):
        pyxel.cls(1)

        pyxel.bltm(0, 0, 0, self.player["x"], self.player["y"], WIDTH, HEIGHT)

        self.draw_props()

        # Aura animée autour des portails
        """for p in self.portals:
            if not p["purified"]:
                if p["type"]=="portal":
                    r = 6 + (pyxel.frame_count % 8)
                    pyxel.circ(p["x"]-self.player["x"]+WIDTH//2, p["y"]-self.player["y"]+HEIGHT//2, r, 13)
                elif p["type"]=="lighthouse":
                    pass
                elif p["type"]=="mansion":
                    pass
        """
        # Portails
        for p in self.portals:
            if p["type"] == "portal":
                pyxel.blt(
                    p["x"] - self.player["x"] + WIDTH // 2 - 8,
                    p["y"] - self.player["y"] + HEIGHT // 2 - 8,
                    2,
                    200
                    + (int(self.hud != "pause") * (pyxel.frame_count % 9) // 3) * 16,
                    0,
                    16,
                    16,
                    0,
                )

            elif p["type"] == "lighthouse":
                pyxel.blt(
                    p["x"] - self.player["x"] + WIDTH // 2,
                    p["y"] - self.player["y"] + HEIGHT // 2,
                    2,
                    0,
                    0,
                    47,
                    111,
                    4,
                )

            elif p["type"] == "mansion":
                pyxel.blt(
                    p["x"] - self.player["x"] + WIDTH // 2,
                    p["y"] - self.player["y"] + HEIGHT // 2,
                    2,
                    48,
                    0,
                    64,
                    40,
                    8,
                )

            elif p["type"] == "mine":
                pyxel.blt(
                    p["x"] - self.player["x"] + WIDTH // 2,
                    p["y"] - self.player["y"] + HEIGHT // 2,
                    2,
                    48,
                    40,
                    19,
                    15,
                    8,
                )

        # Joueur animé
        # col = 7 if self.player["anim"] == 0 else 10

        # Rituel visuel
        if self.ritual_active:
            pyxel.circb(WIDTH // 2, HEIGHT // 2, 20 - self.ritual_progress // 3, 10)

    # -------------------------------

    def draw_spirit(self):
        pyxel.cls(1)

        pyxel.bltm(0, 0, 1, self.player["x"], self.player["y"], WIDTH, HEIGHT)
        portal = self.portals[self.player["portal_id"]]

        """# FOR DEBUG
        for y in range(len(self.path_map)):
            for x in range(len(self.path_map[y])):
                pyxel.text(x*8-self.player["x"]+128+portal["x"]-150, y*8-self.player["y"]+128+portal["y"]-150, str(self.path_map[y][x]), 14)
        
        if self.temp!=[] and self.temp!=None:
            #print(self.temp)
            for tile in self.temp:
                #print(tile[0]*8-self.player["x"]+portal["x"], tile[1]*8-self.player["y"]+portal["y"])
                pyxel.rectb(tile[0]*8-self.player["x"]+portal["x"]-16, tile[1]*8-self.player["y"]+portal["y"]-16, 8, 8, 7)
        """

        self.draw_props()

        for m in self.monsters:
            if (abs(m["vx"]), abs(m["vy"])) != (1, 1):
                pyxel.blt(
                    m["x"] - self.player["x"] + 124,
                    m["y"] - self.player["y"] + 124,
                    1,
                    56 + 8 * m["vx"] * (5 / 3),
                    16 + 8 * m["vy"] * (5 / 3),
                    8,
                    8,
                    7,
                )
            else:
                pyxel.blt(
                    m["x"] - self.player["x"] + 124,
                    m["y"] - self.player["y"] + 124,
                    1,
                    56,
                    24,
                    8,
                    8,
                    7,
                )

        for p in self.projectiles:
            pyxel.circ(
                p["x"] - self.player["x"] + 128, p["y"] - self.player["y"] + 128, 1, 7
            )

        for p in self.projectile_info_impact:
            if p["type"] == "poison_bomb":
                pyxel.blt(
                    p["x"] - self.player["x"] + 120,
                    p["y"] - self.player["y"] + 120,
                    2,
                    self.effect_ui[p["type"]]["x"]
                    + ((pyxel.frame_count - p["impact_frame"]) // 3) * 16,
                    self.effect_ui[p["type"]]["y"],
                    self.effect_ui[p["type"]]["u"],
                    self.effect_ui[p["type"]]["v"],
                    self.effect_ui[p["type"]]["col"],
                )
            elif p["type"] == "cryogenis":
                pyxel.blt(
                    p["x"] - self.player["x"] + 120,
                    p["y"] - self.player["y"] + 120,
                    2,
                    self.effect_ui[p["type"]]["x"],
                    self.effect_ui[p["type"]]["y"],
                    self.effect_ui[p["type"]]["u"],
                    self.effect_ui[p["type"]]["v"],
                    self.effect_ui[p["type"]]["col"],
                )

        if self.player["active_attack"] != None:
            if self.attack_ui[self.player["active_attack"]]["type"] == "closed":
                clipping = 0

                if 128 > pyxel.mouse_x and self.ingame_hud.count(self.hud) == 1:
                    clipping = -16

                if pyxel.frame_count - self.player["cooldown_start_frame"] < 18:
                    tmp = (pyxel.frame_count - self.player["cooldown_start_frame"]) // 3
                    pyxel.blt(
                        128 + 5 + clipping,
                        128 - 3,
                        0,
                        48 + (tmp % 3) * 8,
                        0 + (tmp // 3) * 8 - clipping,
                        8,
                        8,
                        7,
                    )
                else:
                    pyxel.blt(128 + 5 + clipping, 128 - 3, 0, 48, 0 - clipping, 8, 8, 7)

        for h in self.particles:
            pyxel.pset(
                h["x"] - self.player["x"] + 128, h["y"] - self.player["y"] + 128, 7
            )

        for t in self.spirit_particles:
            for i in range(t["h"]):
                pyxel.pset(
                    t["x"] - self.player["x"] + 128,
                    t["y"] - self.player["y"] + 128 + i,
                    t["col"],
                )

    # -------------------------------

    def draw_spirit_sub_zone(self):

        pyxel.cls(9)
        portal = self.portals[self.player["portal_id"]]
        mine = self.mine_path[portal["id"]]

        if portal["type"] == "mine":
            pyxel.bltm(
                0, 0, 2, self.player["x_spirit"], self.player["y_spirit"], WIDTH, HEIGHT
            )
            for p in self.mine_exit:
                pyxel.blt(
                    p["x"] - self.player["x_spirit"] + WIDTH // 2,
                    p["y"] - self.player["y_spirit"] + HEIGHT // 2,
                    2,
                    176,
                    24,
                    19,
                    15,
                    8,
                )
        else:
            # Fond pulsant
            c = 5 + (pyxel.frame_count % 20) // 5

        """ FOR DEBUG
        for y in range(len(self.path_map)):
            for x in range(len(self.path_map[y])):
                pyxel.text(x*8-self.player["x_spirit"]+mine["x"], y*8-self.player["y_spirit"]+mine["y"], str(self.path_map[y][x]), 1)
        
        if self.temp!=[] and self.temp!=None:
            #print(self.temp)
            for tile in self.temp:
                #print(tile[0]*8-self.player["x"]+portal["x"], tile[1]*8-self.player["y"]+portal["y"])
                pyxel.rectb(tile[0]*8-self.player["x_spirit"]+mine["x"], tile[1]*8-self.player["y_spirit"]+mine["y"], 8, 8, 7)
        """

        # Noeuds spirituels
        for n in self.spirit_nodes:
            col = 10 if n["purified"] else 8
            pyxel.circ(
                n["x"] - self.player["x_spirit"] + 128,
                n["y"] - self.player["y_spirit"] + 128,
                3,
                col,
            )

        for m in self.monsters:
            if (abs(m["vx"]), abs(m["vy"])) != (1, 1):
                pyxel.blt(
                    m["x"] - self.player["x_spirit"] + 124,
                    m["y"] - self.player["y_spirit"] + 124,
                    1,
                    56 + 8 * m["vx"] * (5 / 3),
                    16 + 8 * m["vy"] * (5 / 3),
                    8,
                    8,
                    7,
                )
            else:
                pyxel.blt(
                    m["x"] - self.player["x_spirit"] + 124,
                    m["y"] - self.player["y_spirit"] + 124,
                    1,
                    56,
                    24,
                    8,
                    8,
                    7,
                )

        for p in self.projectile_info_impact:
            if p["type"] == "poison_bomb":
                pyxel.blt(
                    p["x"] - self.player["x_spirit"] + 120,
                    p["y"] - self.player["y_spirit"] + 120,
                    2,
                    self.effect_ui[p["type"]]["x"]
                    + ((pyxel.frame_count - p["impact_frame"]) // 3) * 16,
                    self.effect_ui[p["type"]]["y"],
                    self.effect_ui[p["type"]]["u"],
                    self.effect_ui[p["type"]]["v"],
                    self.effect_ui[p["type"]]["col"],
                )
            elif p["type"] == "cryogenis":
                pyxel.blt(
                    p["x"] - self.player["x_spirit"] + 120,
                    p["y"] - self.player["y_spirit"] + 120,
                    2,
                    self.effect_ui[p["type"]]["x"],
                    self.effect_ui[p["type"]]["y"],
                    self.effect_ui[p["type"]]["u"],
                    self.effect_ui[p["type"]]["v"],
                    self.effect_ui[p["type"]]["col"],
                )

        # Projectiles
        for p in self.projectiles:
            pyxel.circ(
                p["x"] - self.player["x_spirit"] + 128,
                p["y"] - self.player["y_spirit"] + 128,
                1,
                7,
            )

        # Joueur
        col = 14 if self.player["anim"] == 0 else 7
        # pyxel.circ(self.player["x"], self.player["y"], 3, col)
        if (self.player["vx"], self.player["vy"]) != (0, 0):
            pyxel.blt(
                120,
                120,
                1,
                16 + 16 * self.player["vx"],
                56 + 48 * self.player["vy"] + ((pyxel.frame_count % 15) // 5) * 16,
                16,
                16,
                7,
            )
        else:
            pyxel.blt(120, 120, 1, 16, 104, 16, 16, 7)

        if self.player["active_attack"] != None:
            if self.attack_ui[self.player["active_attack"]]["type"] == "closed":
                clipping = 0

                if 128 > pyxel.mouse_x and self.ingame_hud.count(self.hud) == 1:
                    clipping = -16

                if pyxel.frame_count - self.player["cooldown_start_frame"] < 18:
                    tmp = (pyxel.frame_count - self.player["cooldown_start_frame"]) // 3
                    pyxel.blt(
                        128 + 6 + clipping * 1.625,
                        128 - 6,
                        1,
                        80 + (tmp % 3) * 16,
                        32 + (tmp // 3) * 16 - clipping * 2,
                        16,
                        16,
                        7,
                    )
                else:
                    pyxel.blt(
                        128 + 6 + clipping * 1.625,
                        128 - 6,
                        1,
                        80,
                        32 - clipping * 2,
                        16,
                        16,
                        7,
                    )

        for h in self.particles:
            pyxel.pset(
                h["x"] - self.player["x_spirit"] + 128,
                h["y"] - self.player["y_spirit"] + 128,
                7,
            )

        # Rituel visuel
        if self.ritual_active:
            pyxel.circb(WIDTH // 2, HEIGHT // 2, 20 - self.ritual_progress // 3, 10)

    # -------------------------------

    def draw_ui(self):
        pyxel.blt(WIDTH - 112, HEIGHT - 60, 2, 56, 56, 104, 56, 7)  # main ui
        if self.player["hp"] > 0:
            pyxel.blt(
                WIDTH - 107,
                HEIGHT - 18,
                2,
                61,
                114,
                66 - (100 - self.player["hp"]) / 100 * 65,
                8,
                7,
            )  # health
        if self.player["faith"] > 0:
            pyxel.blt(
                WIDTH - 40,
                HEIGHT - 52 + (100 - self.player["faith"]) / 100 * 44,
                2,
                160,
                64 + (100 - self.player["faith"]) / 100 * 44,
                32,
                44 - (100 - self.player["faith"]) / 100 * 44,
                7,
            )  # faith

        if self.hud != None:
            if self.hud == "inventory":

                pyxel.blt(74, 144, 2, 0, 152, 108, 62, 0)

                for i in range(3):
                    attack_name = self.player["active_slots"][i]
                    if attack_name != None:
                        item = self.attack_ui[attack_name]
                        pyxel.blt(160, 148 + 19 * i, 2, item["x"], item["y"], 16, 16, 7)
                for i in range(len(self.player["inventory"])):
                    attack_name = self.player["inventory"][i]
                    if attack_name != None:
                        item = self.attack_ui[attack_name]
                        pyxel.blt(
                            78 + (i % 4) * 19,
                            148 + (i // 4) * 19,
                            2,
                            item["x"],
                            item["y"],
                            16,
                            16,
                            7,
                        )

                if self.player["selected_slot"] != [None, None]:
                    if self.player["selected_slot"][0] == "inventory":
                        pyxel.blt(
                            75 + (self.player["selected_slot"][1] % 4) * 19,
                            145 + (self.player["selected_slot"][1] // 4) * 19,
                            2,
                            24,
                            128,
                            24,
                            24,
                            4,
                        )
                    elif self.player["selected_slot"][0] == "active_slots":
                        pyxel.blt(
                            71 + 86,
                            145 + self.player["selected_slot"][1] * 19,
                            2,
                            24,
                            128,
                            24,
                            24,
                            4,
                        )

                if self.player["slot_at_mouse"] != [None, None]:
                    if self.player["slot_at_mouse"][0] == "inventory":
                        # pyxel.rectb(78+(self.player["slot_at_mouse"]%4)*19, 148+(self.player["slot_at_mouse"]//4)*19, 16, 16, 8)
                        pyxel.blt(
                            75 + (self.player["slot_at_mouse"][1] % 4) * 19,
                            145 + (self.player["slot_at_mouse"][1] // 4) * 19,
                            2,
                            0,
                            128,
                            24,
                            24,
                            4,
                        )
                    elif self.player["slot_at_mouse"][0] == "active_slots":
                        pyxel.blt(
                            71 + 86,
                            145 + self.player["slot_at_mouse"][1] * 19,
                            2,
                            0,
                            128,
                            24,
                            24,
                            4,
                        )

            elif self.hud == "pause":
                pyxel.rect(0, 0, 75, HEIGHT, 0)
                for i in range(HEIGHT // 8):
                    pyxel.blt(75, 0 + i * 8, 2, 112, 32, 47, 8, 7)
                for i in range(len(self.pause_ui_text_id)):
                    pyxel.blt(
                        10,
                        20 + i * 30,
                        2,
                        self.pause_ui_text_id[i][0],
                        self.pause_ui_text_id[i][1],
                        self.pause_ui_text_id[i][2],
                        8,
                        3,
                    )
                if self.player["slot_at_mouse"] != [None, None]:
                    slot_id = self.player["slot_at_mouse"][1]
                    pyxel.rectb(
                        9,
                        18 + slot_id * 30,
                        self.pause_ui_text_id[slot_id][2] + 3,
                        13,
                        5,
                    )
                    pyxel.trib(
                        8,
                        19 + slot_id * 30,
                        8,
                        29 + slot_id * 30,
                        3,
                        24 + slot_id * 30,
                        5,
                    )
                    pyxel.trib(
                        self.pause_ui_text_id[slot_id][2] + 12,
                        19 + slot_id * 30,
                        self.pause_ui_text_id[slot_id][2] + 12,
                        29 + slot_id * 30,
                        self.pause_ui_text_id[slot_id][2] + 17,
                        24 + slot_id * 30,
                        5,
                    )
                    pyxel.tri(
                        9,
                        19 + slot_id * 30,
                        9,
                        29 + slot_id * 30,
                        4,
                        24 + slot_id * 30,
                        12,
                    )
                    pyxel.tri(
                        self.pause_ui_text_id[slot_id][2] + 11,
                        19 + slot_id * 30,
                        self.pause_ui_text_id[slot_id][2] + 11,
                        29 + slot_id * 30,
                        self.pause_ui_text_id[slot_id][2] + 16,
                        24 + slot_id * 30,
                        12,
                    )
                    pyxel.rect(
                        9,
                        19 + slot_id * 30,
                        self.pause_ui_text_id[slot_id][2] + 2,
                        11,
                        12,
                    )
                    pyxel.blt(
                        10,
                        20 + slot_id * 30,
                        2,
                        self.pause_ui_text_id[slot_id][0] + 64,
                        self.pause_ui_text_id[slot_id][1],
                        self.pause_ui_text_id[slot_id][2],
                        8,
                        3,
                    )

            elif self.hud == "quit_warning":
                pyxel.rect(0, 0, 75, HEIGHT, 0)
                for i in range(HEIGHT // 8):
                    pyxel.blt(75, 0 + i * 8, 2, 112, 32, 47, 8, 7)
                for i in range(len(self.pause_ui_text_id)):
                    pyxel.blt(
                        10,
                        20 + i * 30,
                        2,
                        self.pause_ui_text_id[i][0],
                        self.pause_ui_text_id[i][1],
                        self.pause_ui_text_id[i][2],
                        8,
                        3,
                    )

                for i in range(12):
                    pyxel.blt(80 + i * 8, 104, 2, 184, 0, 8, 8)
                    pyxel.blt(80 + i * 8, 112 + 4 * 8, 2, 184, 16, 8, 8)

                for i in range(4):
                    pyxel.blt(72, 112 + i * 8, 2, 176, 8, 8, 8)
                    pyxel.blt(80 + 12 * 8, 112 + i * 8, 2, 192, 8, 8, 8)

                for x in range(2):
                    for y in range(2):
                        pyxel.blt(
                            72 + x * 104,
                            104 + y * 40,
                            2,
                            176 + x * 16,
                            0 + y * 16,
                            8,
                            8,
                            0,
                        )

                pyxel.rect(80, 112, 96, 32, 1)

                pyxel.blt(78, 112, 2, 0, 216, 104, 16, 3)

                if self.player["slot_at_mouse"] != [None, None]:
                    slot_id = self.player["slot_at_mouse"][1]
                    pyxel.rectb(95 + slot_id * 48, 132, 16, 13, 5)
                    pyxel.trib(
                        94 + slot_id * 48,
                        133,
                        94 + slot_id * 48,
                        143,
                        89 + slot_id * 48,
                        138,
                        5,
                    )
                    pyxel.trib(
                        111 + slot_id * 48,
                        133,
                        111 + slot_id * 48,
                        143,
                        116 + slot_id * 48,
                        138,
                        5,
                    )
                    pyxel.tri(
                        95 + slot_id * 48,
                        133,
                        95 + slot_id * 48,
                        143,
                        90 + slot_id * 48,
                        138,
                        12,
                    )
                    pyxel.tri(
                        110 + slot_id * 48,
                        133,
                        110 + slot_id * 48,
                        143,
                        115 + slot_id * 48,
                        138,
                        12,
                    )
                    pyxel.rect(95 + slot_id * 48, 133, 16, 11, 12)

                for i in range(2):
                    pyxel.blt(96 + i * 50, 134, 2, 32 - 16 * i, 248, 16 - 5 * i, 8, 15)

            elif self.hud == "settings":
                for i in range(20):
                    pyxel.blt(48 + i * 8, 48, 2, 184, 0, 8, 8)
                    pyxel.blt(48 + i * 8, 56 + 18 * 8, 2, 184, 16, 8, 8)

                for i in range(18):
                    pyxel.blt(40, 56 + i * 8, 2, 176, 8, 8, 8)
                    pyxel.blt(48 + 20 * 8, 56 + i * 8, 2, 192, 8, 8, 8)

                for x in range(2):
                    for y in range(2):
                        pyxel.blt(
                            40 + x * 168,
                            48 + y * 152,
                            2,
                            176 + x * 16,
                            0 + y * 16,
                            8,
                            8,
                            0,
                        )

                pyxel.rect(48, 56, 160, 144, 1)

            elif self.hud == "dead":
                for i in range(20):
                    pyxel.blt(48 + i * 8, 48, 2, 184, 0, 8, 8)
                    pyxel.blt(48 + i * 8, 56 + 18 * 8, 2, 184, 16, 8, 8)

                for i in range(18):
                    pyxel.blt(40, 56 + i * 8, 2, 176, 8, 8, 8)
                    pyxel.blt(48 + 20 * 8, 56 + i * 8, 2, 192, 8, 8, 8)

                for x in range(2):
                    for y in range(2):
                        pyxel.blt(
                            40 + x * 168,
                            48 + y * 152,
                            2,
                            176 + x * 16,
                            0 + y * 16,
                            8,
                            8,
                            0,
                        )

                pyxel.rect(48, 56, 160, 144, 1)

                pyxel.blt(108, 66, 2, 56, 128, 40, 24, 10)

                for x in range(2):
                    ui = self.pause_ui_text_id[x * 4]
                    pyxel.blt(64 + x * 105, 174, 2, ui[0], ui[1], ui[2], 8, 3)

                slot_id = self.player["slot_at_mouse"][1]
                if slot_id != None:
                    ui = self.pause_ui_text_id[slot_id * 4]
                    pyxel.rectb(
                        62 + slot_id * 105,
                        172,
                        self.pause_ui_text_id[slot_id * 4][2] + 4,
                        13,
                        5,
                    )
                    pyxel.rect(
                        63 + slot_id * 105,
                        173,
                        self.pause_ui_text_id[slot_id * 4][2] + 2,
                        11,
                        12,
                    )

                    pyxel.blt(
                        64 + slot_id * 105, 174, 2, ui[0] + 64, ui[1], ui[2], 8, 3
                    )

        for i in range(3):
            attack_name = self.player["active_slots"][i]
            if attack_name != None:
                item = self.attack_ui[attack_name]
                pyxel.blt(
                    WIDTH - 93 + 19 * i, HEIGHT - 34, 2, item["x"], item["y"], 16, 16, 7
                )

            if self.state != STATE_REAL:
                index = (
                    self.player["active_slots"].index(self.player["active_attack"])
                    + (pyxel.mouse_wheel * (int(self.ingame_hud.count(self.hud) == 1)))
                ) % 3
                pyxel.blt(
                    WIDTH - 112 - 3 + self.attack_ui_slot[index][0],
                    HEIGHT - 60 - 3 + self.attack_ui_slot[index][1],
                    2,
                    0,
                    128,
                    24,
                    24,
                    4,
                )

        for i in range(len(self.qol_loot_ui)):
            loot = self.qol_loot_ui[i]
            pyxel.text(25, HEIGHT - 15 + i * 18, str(loot["type"]), 7)
            pyxel.blt(
                5,
                HEIGHT - 20 + i * 18,
                2,
                self.attack_ui[loot["type"]]["x"],
                self.attack_ui[loot["type"]]["y"],
                16,
                16,
                7,
            )

        # pyxel.text(5, HEIGHT - 15, f"HP:{self.player['hp']}", 7)
        # pyxel.text(50, HEIGHT - 15, f"Faith:{self.player['faith']}", 7)

        if self.memory_fragments:
            pyxel.text(5, 5, self.memory_fragments[-1], 6)

    # -------------------------------

    @staticmethod
    def dist(a, b, base_x="x", base_y="y"):
        return ((a[base_x] - b["x"]) ** 2 + (a[base_y] - b["y"]) ** 2) ** 0.5

    @staticmethod
    def heuristic_dist(a, b):
        return 14 * max(abs(a[0] - b[0]), abs(a[1] - b[1])) + 10 * min(
            abs(a[0] - b[0]), abs(a[1] - b[1])
        )


Game()
