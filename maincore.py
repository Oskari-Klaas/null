import pygame
import sys

pygame.init()
#box dimensions
screen_width = 800
screen_height = 600
background_color = (87, 82, 81)
box_color = (147, 112, 219)

#display
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Null")
clock = pygame.time.Clock()

#dimensions and position
player = pygame.Rect(400, 300, 50, 50)

#main application loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(background_color)

    pygame.draw.rect(screen, box_color, player)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()