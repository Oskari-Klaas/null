import pygame, math

def process_collision(player, enemy):
    if not player.alive: return
    if enemy.name == "Warden" and not enemy.touched: return
    if player.rect.colliderect(enemy.rect): player.die()
    if enemy.name == "Reaper":
        dist = math.hypot(player.rect.centerx - enemy.rect.centerx, 
                          player.rect.centery - enemy.rect.centery)
        if dist < enemy.warning_radius: player.die()