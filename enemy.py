import pygame
import math
import random

class Enemy:
    def __init__(self, start_x, start_y, name="Stalker"):
        self.name = name
        self.rect = pygame.Rect(start_x, start_y, 50, 50)
        self.exact_x = float(start_x)
        self.exact_y = float(start_y)
        self.state = "idle"
        self.timer = 0
        self.dir_x, self.dir_y = 0.0, 0.0
        self.speed = 0
        
        self.target_pos = (0, 0)
        self.show_warning = False

        if self.name == "Stalker": self.color = (255, 50, 50)
        elif self.name == "Sentinel": self.color = (0, 255, 255)
        elif self.name == "Ghost": self.color = (220, 220, 220)
        elif self.name == "Pulse": self.color = (255, 255, 0)
        elif self.name == "Reaper": self.color = (138, 43, 226)
        elif self.name == "Void": self.color = (20, 20, 20); self.rect.size = (40, 40)

    def update(self, player_rect):
        self.timer += 1
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        # 1. STALKER (Standard Dash)
        if self.name == "Stalker":
            if self.state == "idle" and self.timer > 90:
                self.state = "windup"; self.timer = 0
                if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist
            elif self.state == "windup" and self.timer > 30:
                self.state = "active"; self.timer = 0
            elif self.state == "active":
                self.speed = 10
                if self.timer > 22: # Long dash maintained
                    self.state = "idle"; self.timer = 0; self.speed = 0

        # 2. SENTINEL
        elif self.name == "Sentinel":
            self.state = "active"; self.speed = 3.0
            if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist

        # 3. GHOST
        elif self.name == "Ghost":
            self.state = "active"
            self.speed = 4.5 if dist > 150 else 1.5
            if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist

        # 4. PULSE
        elif self.name == "Pulse":
            self.state = "active"
            p_val = math.sin(pygame.time.get_ticks() * 0.005) * 35
            self.rect.size = (50 + int(p_val), 50 + int(p_val))
            self.speed = 1.8
            if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist

        # 5. REAPER
        elif self.name == "Reaper":
            self.state = "active"; self.speed = 0
            if self.timer == 90: 
                self.target_pos = (player_rect.centerx + random.randint(-100, 100), 
                                  player_rect.centery + random.randint(-100, 100))
                self.target_pos = (max(50, min(750, self.target_pos[0])), 
                                  max(50, min(550, self.target_pos[1])))
                self.show_warning = True
            elif self.timer > 150:
                self.exact_x, self.exact_y = self.target_pos
                self.show_warning = False; self.timer = 0

        # 6. VOID
        elif self.name == "Void":
            self.state = "active"; self.speed = 0

        # Movement and Bouncing logic
        self.exact_x += self.dir_x * self.speed
        self.exact_y += self.dir_y * self.speed

        if self.exact_x < 0: self.exact_x = 0; self.dir_x *= -1
        if self.exact_x > 800 - self.rect.width: self.exact_x = 800 - self.rect.width; self.dir_x *= -1
        if self.exact_y < 0: self.exact_y = 0; self.dir_y *= -1
        if self.exact_y > 600 - self.rect.height: self.exact_y = 600 - self.rect.height; self.dir_y *= -1

        self.rect.x, self.rect.y = int(self.exact_x), int(self.exact_y)

    def draw(self, screen):
        if self.name == "Reaper" and self.show_warning:
            pygame.draw.circle(screen, (255, 0, 0), self.target_pos, 40, 2)
        pygame.draw.rect(screen, self.color, self.rect)
        if self.name == "Stalker" and self.state == "windup":
            pygame.draw.line(screen, self.color, self.rect.center, (self.rect.centerx + self.dir_x*2000, self.rect.centery + self.dir_y*2000), 2)