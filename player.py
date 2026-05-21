import pygame

class Player:
    # 1. The Hardware Setup (Runs once when the player spawns)
    def __init__(self, start_x, start_y):
        self.color = (147, 112, 219)
        self.speed = 5
        # This creates the physical hitbox exactly like you did before
        self.rect = pygame.Rect(start_x, start_y, 50, 50)

    # 2. check for W A S D input
    def move(self, keys):
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed

        #checking for walls

        if self.rect.x < 0:
            self.rect.x = 0

        if self.rect.x > 750:
            self.rect.x = 750

        if self.rect.y < 0:
            self.rect.y = 0

        if self.rect.y > 550:
            self.rect.y = 550
    
    # 3. The Render Command
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
