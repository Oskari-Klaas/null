import pygame

class Enemy:

    def __init__(self, start_x, start_y):
        self.color = (255, 0, 0)
        self.speed = 0
        self.state = "idle"
        self.timer = 0
        self.dash_dir_x = 0
        self.dash_dir_y = 0
        self.rect = pygame.Rect(start_x, start_y, 50, 50)
        

    def update(self, player_rect):
        if self.state == "idle":
            self.timer += 1
            if self.timer > 120:  # After 2 seconds, switch to dash
                self.state = "dashing"
                self.timer = 0
                #enemy movement
                if player_rect.x > self.rect.x:
                    self.dash_dir_x = 1
                elif player_rect.x < self.rect.x:
                    self.dash_dir_x = -1
                else:
                    self.dash_dir_x = 0

                if player_rect.y > self.rect.y:
                    self.dash_dir_y = 1
                elif player_rect.y < self.rect.y:
                    self.dash_dir_y = -1
                else:
                    self.dash_dir_y = 0


        if self.state == "dashing":
            self.speed = 6
            self.timer += 1
            if self.timer > 30:
                self.state = "idle"
                self.speed = 0
                self.timer = 0
                
        self.rect.x += self.dash_dir_x * self.speed
        self.rect.y += self.dash_dir_y * self.speed
        

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)