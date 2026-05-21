import pygame

class Player:
    def __init__(self, start_x, start_y):
        self.color = (147, 112, 219) # Purple
        self.speed = 5
        self.rect = pygame.Rect(start_x, start_y, 50, 50)
        self.alive = True 

    def move(self, keys):
        if not self.alive: 
            return 

        if keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_d]: self.rect.x += self.speed
        if keys[pygame.K_w]: self.rect.y -= self.speed
        if keys[pygame.K_s]: self.rect.y += self.speed

        # Screen boundaries
        if self.rect.x < 0: self.rect.x = 0
        if self.rect.x > 750: self.rect.x = 750
        if self.rect.y < 0: self.rect.y = 0
        if self.rect.y > 550: self.rect.y = 550

    def die(self):
        self.alive = False
        self.color = (50, 50, 50) # Gray
        print("GAME OVER!")

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)