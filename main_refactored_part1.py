import pyxel
import math
import random

WIDTH, HEIGHT = 256, 256

STATE_REAL = 0
STATE_SPIRIT = 1
STATE_SPIRIT_SUB_ZONE = 2


class PlayerData:
    """Encapsulates all player-related data"""
    def __init__(self):
        self.x = 38 * 8 - 128
        self.y = 18 * 8 - 128
        self.x_spirit = 100
        self.y_spirit = 100
        self.vx = 0
        self.vy = 0
        self.hp = 100
        self.max_hp = 100
        self.faith = 100
        self.max_faith = 100
        self.inventory = [None] * 12
        self.active_slots = ["sword", None, None]
        self.anim = 0
        self.portal_id = None
        self.immortality = False
        self.immortality_start_frame = 0
        self.cooldown = False
        self.cooldown_start_frame = 0
        self.active_attack = "sword"
        self.slot_at_mouse = [None, None]
        self.selected_slot = [None, None]

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "x_spirit": self.x_spirit,
            "y_spirit": self.y_spirit,
            "vx": self.vx,
            "vy": self.vy,
            "hp": self.hp,
            "faith": self.faith,
            "inventory": self.inventory,
            "active_slots": self.active_slots,
            "anim": self.anim,
            "portal_id": self.portal_id,
            "immortality": self.immortality,
            "immortality_start_frame": self.immortality_start_frame,
            "cooldown": self.cooldown,
            "cooldown_start_frame": self.cooldown_start_frame,
            "active_attack": self.active_attack,
            "slot_at_mouse": self.slot_at_mouse,
            "selected_slot": self.selected_slot,
        }

    def from_dict(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


