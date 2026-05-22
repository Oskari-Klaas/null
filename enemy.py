import math
import random

import pygame


ENEMY_COLORS = {
    "Stalker": (255, 50, 50),
    "Sentinel": (0, 255, 255),
    "Drifter": (95, 210, 255),
    "The Weaver": (170, 95, 255),
    "Ghost": (220, 220, 220),
    "Pulse": (255, 255, 0),
    "Reaper": (138, 43, 226),
    "Void": (20, 20, 20),
    "Stoplight": (255, 0, 0),
    "Warden": (60, 30, 10),
}


def enemy_color(name):
    return ENEMY_COLORS.get(name, (200, 200, 200))


def outline_color(fill):
    brightness = fill[0] * 0.299 + fill[1] * 0.587 + fill[2] * 0.114
    return (245, 245, 255) if brightness < 80 else (12, 12, 16)


def buff_level_for(round_num):
    return max(0, (round_num - 5) // 5)


def buff_mult_for(round_num):
    return 1.0 + buff_level_for(round_num) * 0.18


class Enemy:
    def __init__(self, start_x, start_y, name="Stalker"):
        self.name = name
        self.rect = pygame.Rect(start_x, start_y, 50, 50)
        if self.name == "Void":
            self.rect.size = (40, 40)

        self.exact_x = float(self.rect.x)
        self.exact_y = float(self.rect.y)
        self.state = "idle"
        self.timer = 0
        self.dir_x, self.dir_y = 0.0, 0.0
        self.speed = 0
        self.color = enemy_color(name)

        self.target_pos = (0, 0)
        self.show_warning = False
        self.touched = False
        self.base_size = 50
        self.stand_timer = 0
        self.lane_axis = random.choice(["x", "y"])
        self.link_active = False
        self.thread_tense = False
        self.tension_timer = 0
        self.thread_radius = 640
        self.tension_limit = 120
        self.drift_origin_x = self.exact_x
        self.drift_origin_y = self.exact_y

    def choose_drifter_direction(self, blocked=None):
        if blocked is None:
            blocked = []

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        options = [direction for direction in directions if direction not in blocked]
        self.dir_x, self.dir_y = random.choice(options or directions)
        self.lane_axis = "x" if self.dir_x != 0 else "y"
        self.drift_origin_x = self.exact_x
        self.drift_origin_y = self.exact_y

    def drifted_half_axis(self):
        if self.lane_axis == "x":
            return abs(self.exact_x - self.drift_origin_x) >= 400
        return abs(self.exact_y - self.drift_origin_y) >= 300

    def update(self, player_rect, round_num=1, collectibles=None):
        if collectibles is None:
            collectibles = []

        self.timer += 1
        buff_level = buff_level_for(round_num)
        mult = buff_mult_for(round_num)
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if self.name == "Stoplight":
            if self.state == "idle" and self.timer > 600 / mult:
                self.state = "warning"
                self.timer = 0
                self.stand_timer = 0
            elif self.state == "warning" and self.timer > max(90, int(150 / (1 + buff_level * 0.12))):
                self.state = "check"
                self.timer = 0
            elif self.state == "check" and self.timer > 30:
                self.state = "idle"
                self.timer = 0
            return

        if self.name == "Stalker":
            if self.state == "idle":
                self.speed = 0
                if self.timer > 90 / mult:
                    self.state = "windup"
                    self.timer = 0
                    if dist != 0:
                        self.dir_x, self.dir_y = dx / dist, dy / dist
            elif self.state == "windup":
                self.speed = 0
                if self.timer > max(16, int(30 / mult)):
                    self.state = "active"
                    self.timer = 0
            elif self.state == "active":
                self.speed = 10 * mult
                if self.timer > 22 + buff_level * 2:
                    self.state = "idle"
                    self.timer = 0
                    self.speed = 0

        elif self.name == "Sentinel":
            self.state = "active"
            self.speed = min(4.85, 3.2 + buff_level * 0.35)
            if dist != 0:
                self.dir_x, self.dir_y = dx / dist, dy / dist

        elif self.name == "Drifter":
            self.state = "active"
            self.speed = 2.15 * mult
            turn_frames = max(70, int(150 / mult))
            can_turn = self.drifted_half_axis()
            if (self.dir_x == 0 and self.dir_y == 0) or (self.timer > turn_frames and can_turn):
                self.choose_drifter_direction()
                self.timer = 0

        elif self.name == "The Weaver":
            self.state = "active"
            self.speed = 0
            self.thread_radius = max(155, 620 - buff_level * 85)
            self.tension_limit = max(58, 112 - buff_level * 12)
            link_frames = max(120, int(300 / mult))
            if not self.link_active and self.timer > link_frames:
                self.link_active = True
                self.thread_tense = False
                self.tension_timer = 0
                self.timer = 0

        elif self.name == "Ghost":
            self.state = "active"
            self.speed = max(1.5, 3 - (dist / 100)) * mult
            if dist != 0:
                self.dir_x, self.dir_y = dx / dist, dy / dist

        elif self.name == "Pulse":
            self.state = "active"
            self.speed = 2.05 * mult
            if dist != 0:
                self.dir_x, self.dir_y = dx / dist, dy / dist

            old_center = self.rect.center
            pulse_period = max(48, int(90 / (1 + buff_level * 0.12)))
            phase = (self.timer % pulse_period) / pulse_period
            new_size = int(self.base_size + math.sin(math.pi * phase) * (30 + buff_level * 4))
            self.rect.size = (new_size, new_size)
            self.rect.center = old_center
            self.exact_x = float(self.rect.x)
            self.exact_y = float(self.rect.y)

        elif self.name == "Reaper":
            self.state = "active"
            self.speed = 0
            wait_frames = max(45, int(150 / mult))
            telegraph_frames = max(24, int(60 / (1 + buff_level * 0.15)))

            if not self.show_warning and self.timer > wait_frames:
                offset = max(35, 80 - buff_level * 8)
                self.target_pos = (
                    player_rect.centerx + random.randint(-offset, offset),
                    player_rect.centery + random.randint(-offset, offset),
                )
                self.target_pos = (
                    max(50, min(750, self.target_pos[0])),
                    max(50, min(550, self.target_pos[1])),
                )
                self.show_warning = True
                self.timer = 0
            elif self.show_warning and self.timer > telegraph_frames:
                self.exact_x = float(self.target_pos[0] - self.rect.width // 2)
                self.exact_y = float(self.target_pos[1] - self.rect.height // 2)
                self.show_warning = False
                self.timer = 0

        elif self.name == "Void":
            self.state = "active"
            self.speed = 0

        self._move_and_bounce()

    def _move_and_bounce(self):
        if self.name in ["Void", "Warden", "Stoplight", "Reaper"] or self.speed == 0:
            self.rect.topleft = (int(self.exact_x), int(self.exact_y))
            return

        self.exact_x += self.dir_x * self.speed
        self.exact_y += self.dir_y * self.speed

        if self.name in ["Sentinel", "Pulse"]:
            self.exact_x = max(0, min(self.exact_x, 800 - self.rect.width))
            self.exact_y = max(0, min(self.exact_y, 600 - self.rect.height))
            self.rect.topleft = (int(self.exact_x), int(self.exact_y))
            return

        blocked = []
        if self.exact_x < 0:
            self.exact_x = 0
            blocked.append((-1, 0))
            self.dir_x *= -1
        if self.exact_x > 800 - self.rect.width:
            self.exact_x = 800 - self.rect.width
            blocked.append((1, 0))
            self.dir_x *= -1
        if self.exact_y < 0:
            self.exact_y = 0
            blocked.append((0, -1))
            self.dir_y *= -1
        if self.exact_y > 600 - self.rect.height:
            self.exact_y = 600 - self.rect.height
            blocked.append((0, 1))
            self.dir_y *= -1

        if self.name == "Drifter" and blocked and self.drifted_half_axis():
            self.choose_drifter_direction(blocked)

        self.rect.topleft = (int(self.exact_x), int(self.exact_y))

    def draw(self, screen):
        if self.name == "Stoplight":
            return

        if self.name == "Reaper" and self.show_warning:
            pygame.draw.circle(screen, (255, 0, 0), self.target_pos, 40, 2)

        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, outline_color(self.color), self.rect, 2)

        if self.name == "Drifter":
            if self.lane_axis == "x":
                pygame.draw.line(screen, (45, 110, 135), (0, self.rect.centery), (800, self.rect.centery), 2)
                pygame.draw.line(screen, (12, 12, 16), self.rect.midleft, self.rect.midright, 4)
            else:
                pygame.draw.line(screen, (45, 110, 135), (self.rect.centerx, 0), (self.rect.centerx, 600), 2)
                pygame.draw.line(screen, (12, 12, 16), self.rect.midtop, self.rect.midbottom, 4)

        if self.name == "The Weaver":
            pygame.draw.line(screen, (12, 12, 16), self.rect.midleft, self.rect.midright, 3)
            pygame.draw.line(screen, (12, 12, 16), self.rect.midtop, self.rect.midbottom, 3)
            pygame.draw.circle(screen, (12, 12, 16), self.rect.center, 10)

        if self.name == "Warden":
            core = self.rect.inflate(-22, -22)
            pygame.draw.rect(screen, (255, 210, 115), core)
            pygame.draw.rect(screen, (12, 12, 16), core, 2)

        if self.name == "Stalker" and self.state == "windup":
            pygame.draw.line(
                screen,
                self.color,
                self.rect.center,
                (
                    self.rect.centerx + self.dir_x * 2000,
                    self.rect.centery + self.dir_y * 2000,
                ),
                2,
            )
