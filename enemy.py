import pygame, math, random

class Enemy:
    def __init__(self, start_x, start_y, name="Stalker"):
        self.name, self.rect = name, pygame.Rect(start_x, start_y, 50, 50)
        self.exact_x, self.exact_y = float(start_x), float(start_y)
        self.state, self.timer = "idle", 0
        self.dir_x, self.dir_y, self.speed = 0.0, 0.0, 0
        self.touched = False 
        self.base_size, self.stand_timer = 50, 30

        colors = {"Void": (0,0,0), "Warden": (60,30,10), "Magnet": (128,128,128),
                  "Stalker": (0,0,255), "Sentinel": (0,0,139), "Glitch": (255,255,0),
                  "Reaper": (40,40,40), "Pulse": (255,100,255)}
        self.color = colors.get(name, (200,200,200))

    def update(self, player_rect, round_num, collectibles=[]):
        self.timer += 1
        mult = 1.0 + (round_num // 10) * 0.20
        dx, dy = player_rect.centerx - self.rect.centerx, player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if self.name == "Stoplight":
            if self.state == "idle" and self.timer > 600/mult: 
                self.state, self.timer, self.stand_timer = "warning", 0, 30
            elif self.state == "warning" and self.timer > 200: self.state, self.timer = "check", 0
            elif self.state == "check" and self.timer > 30: self.state, self.timer = "idle", 0
            return

        if self.name == "Pulse":
            self.speed = 1.5 * mult
            if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist
            phase = (self.timer % 90) / 90.0
            size_offset = math.sin(math.pi * phase) * 30 
            new_size = int(self.base_size + size_offset)
            cx, cy = self.rect.center
            self.rect = pygame.Rect(0, 0, new_size, new_size)
            self.rect.center = (cx, cy)

        elif self.name == "Stalker":
            if self.state == "idle":
                if not hasattr(self, 'wait_time'): self.wait_time = random.randint(60, 180) / mult
                if self.timer > self.wait_time:
                    self.state, self.timer = "windup", 0
                    if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist
            elif self.state == "windup" and self.timer > 40: self.state, self.timer = "active", 0
            elif self.state == "active":
                self.speed = 15 * mult
                if self.timer > 20: 
                    self.state, self.timer, self.speed = "idle", 0, 0
                    if hasattr(self, 'wait_time'): delattr(self, 'wait_time')

        elif self.name == "Reaper":
            self.speed = 1.6 * mult
            if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist
            self.warning_radius = 80 + math.sin(pygame.time.get_ticks()*0.01)*10

        elif self.name in ["Sentinel", "Glitch", "Magnet"]:
            self.speed = 2.0 * mult
            if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist
            if self.name == "Magnet":
                for c in collectibles:
                    cdx, cdy = self.rect.centerx - c.centerx, self.rect.centery - c.centery
                    if math.hypot(cdx, cdy) < 300: c.x += (cdx/math.hypot(cdx, cdy))*2.8

        if self.name not in ["Void", "Warden", "Stoplight"]:
            self.exact_x += self.dir_x * self.speed
            self.exact_y += self.dir_y * self.speed
            if self.name != "Pulse": self.rect.topleft = (int(self.exact_x), int(self.exact_y))
            else: self.rect.center = (int(self.exact_x + 25), int(self.exact_y + 25))

    def draw(self, screen):
        if self.name == "Stoplight":
            color = (255, 255, 0) if self.state == "warning" else (255, 0, 0)
            if self.state != "idle": pygame.draw.circle(screen, color, self.rect.center, 30)
        else: pygame.draw.rect(screen, self.color, self.rect)