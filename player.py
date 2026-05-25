import pygame


class Player:
    def __init__(self, start_x, start_y):
        self.color = (147, 112, 219)
        self.speed = 5
        self.rect = pygame.Rect(start_x, start_y, 50, 50)
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.alive = True
        self.moving = False

    def set_position(self, x, y, center=False):
        if center:
            self.rect.center = (x, y)
        else:
            self.rect.topleft = (x, y)
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

    def move(self, keys, pull_x=0, pull_y=0):
        if not self.alive:
            return

        right = int(bool(keys[pygame.K_d] or keys[pygame.K_RIGHT]))
        left = int(bool(keys[pygame.K_a] or keys[pygame.K_LEFT]))
        down = int(bool(keys[pygame.K_s] or keys[pygame.K_DOWN]))
        up = int(bool(keys[pygame.K_w] or keys[pygame.K_UP]))
        
        dx = (right - left) * self.speed
        dy = (down - up) * self.speed
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        
        self.moving = dx != 0 or dy != 0

        self.pos_x += dx + pull_x
        self.pos_y += dy + pull_y
        self.pos_x = max(0, min(self.pos_x, 800 - self.rect.width))
        self.pos_y = max(0, min(self.pos_y, 600 - self.rect.height))
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def die(self):
        self.alive = False
        self.color = (50, 50, 50)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (245, 245, 255), self.rect, 2)
