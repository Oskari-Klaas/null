import pygame

def process_collision(player, enemy):
    # If player is still alive and enemy is dashing...
    if player.alive and enemy.state == "dashing":
        # Check for the hit
        if player.rect.colliderect(enemy.rect):
            player.die()