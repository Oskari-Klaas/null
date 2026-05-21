import time
import pygame
import sys
import enemy
import player
import damage 

pygame.init()

screen_width = 800
screen_height = 600
background_color = (87, 82, 81)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Null")
clock = pygame.time.Clock()

player_box = player.Player(400, 300)
enemy_box = enemy.Enemy(100, 100)


#main application loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # 1. Logic
    player_box.move(keys)
    enemy_box.update(player_box.rect)
    
    # 2. Collision Check
    damage.process_collision(player_box, enemy_box)

    # 3. Render
    screen.fill(background_color)
    player_box.draw(screen)
    enemy_box.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()