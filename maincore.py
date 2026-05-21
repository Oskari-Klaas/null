import pygame
import sys
import enemy
import player
import damage
import random
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)

player_box = player.Player(400, 500)
enemies = [] 
game_state = "choosing" 
round_timer = 0

enemy_pool = ["Stalker", "Sentinel", "Ghost", "Pulse", "Reaper", "Void"]
current_choices = []

def refresh_choices():
    global current_choices
    current_choices = random.sample(enemy_pool, 3)

refresh_choices()

choices_rects = [pygame.Rect(125, 250, 100, 100), pygame.Rect(350, 250, 100, 100), pygame.Rect(575, 250, 100, 100)]

def start_new_round(name):
    global game_state, round_timer, enemies
    enemies.append(enemy.Enemy(random.randint(100, 700), random.randint(50, 200), name))
    for e in enemies:
        if e.name != "Void":
            e.exact_x, e.exact_y = random.randint(100, 700), random.randint(50, 150)
        e.state = "idle"; e.timer = random.randint(0, 30); e.speed = 0
    player_box.rect.center = (400, 500)
    round_timer = 7 * 60 
    game_state = "running"

while True:
    screen.fill((30, 30, 30))
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()

    if game_state == "running" and player_box.alive:
        for e in enemies:
            if e.name == "Void":
                dx, dy = e.rect.centerx - player_box.rect.centerx, e.rect.centery - player_box.rect.centery
                dist = math.hypot(dx, dy)
                if dist < 200:
                    player_box.rect.x += int(dx * 0.03); player_box.rect.y += int(dy * 0.03)

        player_box.move(keys)
        for e in enemies:
            e.update(player_box.rect)
            damage.process_collision(player_box, e)
        
        round_timer -= 1
        if round_timer <= 0:
            game_state = "choosing"; refresh_choices(); player_box.rect.center = (400, 500)

        player_box.draw(screen)
        for e in enemies: e.draw(screen)
        screen.blit(font.render(f"TIME: {round_timer//60}s | ROUND: {len(enemies)}", True, (255,255,255)), (20, 20))

    elif game_state == "choosing":
        player_box.move(keys)
        player_box.draw(screen)
        for i, box in enumerate(choices_rects):
            pygame.draw.rect(screen, (200, 200, 200), box, 3)
            screen.blit(font.render(current_choices[i], True, (255,255,255)), (box.x + 5, box.y - 30))
            if player_box.rect.colliderect(box): start_new_round(current_choices[i])

    if not player_box.alive:
        screen.blit(font.render("DIED! PRESS 'R' TO RESTART", True, (255, 50, 50)), (280, 150))
        if keys[pygame.K_r]:
            player_box = player.Player(400, 500); enemies = []; refresh_choices(); game_state = "choosing"

    pygame.display.flip()
    clock.tick(60)