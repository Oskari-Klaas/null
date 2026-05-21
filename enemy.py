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

        # Unique traits based on Name
        if self.name == "Stalker":
            self.color = (255, 50, 50) # Bright Red
        elif self.name == "Sentinel":
            self.color = (0, 255, 255) # Cyan
        elif self.name == "Frag":
            self.color = (255, 165, 0) # Orange
            self.rect.size = (40, 40) # Starts smaller

    def update(self, player_rect):
        self.timer += 1

        # STALKER: Dashing Logic
        if self.name == "Stalker":
            if self.state == "idle" and self.timer > 90:
                self.state = "windup"; self.timer = 0
                dx = player_rect.centerx - self.rect.centerx
                dy = player_rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist
            elif self.state == "windup" and self.timer > 30:
                self.state = "active"; self.timer = 0
            elif self.state == "active":
                self.speed = 10
                if self.timer > 22: self.state = "idle"; self.timer = 0; self.speed = 0

        # SENTINEL: Constant Pressure Logic
        elif self.name == "Sentinel":
            self.state = "active"
            self.speed = 1.0
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist

        # FRAG: Proximity Speed Logic (Balanced alternative to teleporting)
        elif self.name == "Frag":
            self.state = "active"
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            # Gets faster the closer it is, but caps at speed 6
            self.speed = max(1.5, 3 - (dist / 100)) 
            if dist != 0: self.dir_x, self.dir_y = dx/dist, dy/dist

        self.exact_x += self.dir_x * self.speed
        self.exact_y += self.dir_y * self.speed
        self.rect.x, self.rect.y = int(self.exact_x), int(self.exact_y)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.name == "Stalker" and self.state == "windup":
            end_x = self.rect.centerx + (self.dir_x * 2000)
            end_y = self.rect.centery + (self.dir_y * 2000)
            pygame.draw.line(screen, self.color, self.rect.center, (end_x, end_y), 2)