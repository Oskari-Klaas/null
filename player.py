import pygame


"""Player character representation and movement helper methods."""


class Player:
    def __init__(self, start_x, start_y):
        """Create a player at the given start position."""
        self.color = (147, 112, 219)
        self.speed = 5
        self.rect = pygame.Rect(start_x, start_y, 50, 50)
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.alive = True
        self.moving = False

    def set_position(self, x, y, center=False):
        """Move the player instantly to a new position."""
        if center:
            self.rect.center = (x, y)
        else:
            self.rect.topleft = (x, y)
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

    def move(self, keys, pull_x=0, pull_y=0):
        """Update player movement based on input keys and external forces."""
        if not self.alive:
            return

        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * self.speed
        dy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.speed
        self.moving = dx != 0 or dy != 0

        self.pos_x += dx + pull_x
        self.pos_y += dy + pull_y
        self.pos_x = max(0, min(self.pos_x, 800 - self.rect.width))
        self.pos_y = max(0, min(self.pos_y, 600 - self.rect.height))
        self.rect.topleft = (int(self.pos_x), int(self.pos_y))

    def die(self):
        """Mark the player as dead and change the visual appearance."""
        self.alive = False
        self.color = (50, 50, 50)

    def draw(self, screen):
        """Render the player rectangle to the given surface."""
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (245, 245, 255), self.rect, 2)
