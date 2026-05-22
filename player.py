import pygame

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.pos_x, self.pos_y = float(x), float(y)
        self.speed, self.alive, self.moving = 4.5, True, False

    def move(self, keys, px=0, py=0):
        if not self.alive: return
        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * self.speed
        dy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.speed
        self.moving = (dx != 0 or dy != 0)
        self.pos_x += dx + px; self.pos_y += dy + py
        self.pos_x = max(0, min(self.pos_x, 760))
        self.pos_y = max(0, min(self.pos_y, 560))
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def die(self): self.alive = False
    def draw(self, screen): pygame.draw.rect(screen, (0,255,0) if self.alive else (100,100,100), self.rect)