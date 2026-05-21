import pygame
import math

class Enemy:
    def __init__(self, start_x, start_y):
        self.color = (255, 0, 0)
        self.speed = 0
        self.state = "idle"
        self.timer = 0
        self.dash_dir_x = 0.0
        self.dash_dir_y = 0.0
        self.rect = pygame.Rect(start_x, start_y, 50, 50)

        self.exact_x = float(start_x)
        self.exact_y = float(start_y)
        

    def update(self, player_rect):
        if self.state == "idle":
            self.timer += 1
            if self.timer > 120:  # After 2 seconds, switch to dash
                self.state = "windup"
                self.timer = 0

                # Enemy shmovement logic
                dx = player_rect.centerx - self.rect.centerx
                dy = player_rect.centery - self.rect.centery
                distance = math.hypot(dx, dy)

                distance = math.hypot(dx, dy)

                if distance != 0:
                    self.dash_dir_x = dx / distance
                    self.dash_dir_y = dy / distance
                else:
                    self.dash_dir_x = 0
                    self.dash_dir_y = 0

        elif self.state == "windup":
            self.timer += 1
            if self.timer > 30:  # After 0.5 seconds, switch to dash
                self.state = "dashing"
                self.timer = 0


        elif self.state == "dashing":
            self.speed = 6
            if self.timer > 120: 
                self.state = "dashing"
                self.timer = 0
                
                # Aim at player position
                if player_rect.x > self.rect.x: self.dash_dir_x = 1
                elif player_rect.x < self.rect.x: self.dash_dir_x = -1
                else: self.dash_dir_x = 0

                if player_rect.y > self.rect.y: self.dash_dir_y = 1
                elif player_rect.y < self.rect.y: self.dash_dir_y = -1
                else: self.dash_dir_y = 0

        if self.state == "dashing":
            self.speed = 8
            self.timer += 1
            if self.timer > 30:
                self.state = "idle"
                self.speed = 0
                self.timer = 0

        self.exact_x += self.dash_dir_x * self.speed
        self.exact_y += self.dash_dir_y * self.speed

        self.rect.x = int(self.exact_x)
        self.rect.y = int(self.exact_y)
        
                
        self.rect.x += self.dash_dir_x * self.speed
        self.rect.y += self.dash_dir_y * self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

        if self.state == "windup":
            end_x = self.rect.centerx + (self.dash_dir_x * 2000)
            end_y = self.rect.centery + (self.dash_dir_y * 2000)
            pygame.draw.line(screen, self.color, self.rect.center, (end_x, end_y), 3)