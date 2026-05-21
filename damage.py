import pygame
def process_collision(player, enemy):
    if player.alive and enemy.state == "active":
        if player.rect.colliderect(enemy.rect):
            player.die()