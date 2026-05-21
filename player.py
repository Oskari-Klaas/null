import pygame

class Player:
    def __init__(self, start_x, start_y):
        self.color = (147, 112, 219) # Purple
        self.speed = 5
        self.rect = pygame.Rect(start_x, start_y, 50, 50)
        self.alive = True 

    def move(self, keys):
        if not self.alive: return 

        if keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_d]: self.rect.x += self.speed
        if keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_s]: self.rect.y += self.speed

        # Screen boundaries
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > 800: self.rect.right = 800
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > 600: self.rect.bottom = 600

    def die(self):
        self.alive = False
        self.color = (50, 50, 50)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)