import time
import pygame
import sys
import enemy
import player

#somthing

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

#creates da player
player_box = player.Player(400, 300)

#creates enemy
enemy_box = enemy.Enemy(100, 100)


#main application loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    player_box.move(keys)

    enemy_box.update(player_box.rect)

    screen.fill(background_color)

    player_box.draw(screen)

    enemy_box.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()