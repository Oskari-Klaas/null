import pygame
import sys
import enemy
import player
import damage
import random

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Nullscape: Evolution")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 22)

player_box = player.Player(400, 500)
enemies = [] 
game_state = "choosing" # NEW NAME
round_timer = 0

# Names for the choice buttons
enemy_names = ["Stalker", "Sentinel", "Frag"]
choices = [
    pygame.Rect(150, 250, 90, 90),
    pygame.Rect(355, 250, 90, 90),
    pygame.Rect(560, 250, 90, 90)
]

def start_new_round(name):
    global game_state, round_timer, enemies
    enemies.append(enemy.Enemy(400, 100, name))
    
    for e in enemies:
        e.exact_x, e.exact_y = random.randint(50, 750), random.randint(50, 150)
        e.state = "idle"
        e.timer = random.randint(0, 60)
        e.speed = 0
        
    player_box.rect.center = (400, 500)
    round_timer = 30 * 60 
    game_state = "running" # NEW NAME

running_bool = True # Separate from game_state to handle the app window
while running_bool:
    screen.fill((87, 82, 81))
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running_bool = False

    if game_state == "running" and player_box.alive:
        player_box.move(keys)
        for e in enemies:
            e.update(player_box.rect)
            damage.process_collision(player_box, e)
        
        round_timer -= 1
        if round_timer <= 0:
            game_state = "choosing"
            player_box.rect.center = (400, 500)

        player_box.draw(screen)
        for e in enemies: e.draw(screen)
        
        timer_txt = font.render(f"SURVIVE: {round_timer//60}s | Round: {len(enemies)}", True, (255,255,255))
        screen.blit(timer_txt, (15, 15))

    elif game_state == "choosing":
        player_box.move(keys)
        player_box.draw(screen)
        for i, box in enumerate(choices):
            pygame.draw.rect(screen, (255, 255, 255), box, 2)
            name_label = font.render(enemy_names[i], True, (255,255,255))
            screen.blit(name_label, (box.x + 5, box.y - 30))
            if player_box.rect.colliderect(box):
                start_new_round(enemy_names[i])

    if not player_box.alive:
        msg = font.render("DIED! PRESS 'R' TO RESTART", True, (255, 50, 50))
        screen.blit(msg, (280, 150))
        if keys[pygame.K_r]:
            player_box = player.Player(400, 500)
            enemies = [] 
            game_state = "choosing"

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()