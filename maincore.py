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

#main application loop
running = True
game_state = "menu"
play_button = pygame.Rect(100, 250, 200, 80)
exit_button = pygame.Rect(500, 250, 200, 80)

font = pygame.font.SysFont(None, 48)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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

    # --- 1. UNIVERSAL LOGIC ---
    # The player can ALWAYS move, so you can walk into the buttons
    player_box.move(keys)

    # --- 2. THE STATE MACHINE FIREWALL ---
    if game_state == "menu":
        # If player walks into the PLAY button
        if player_box.rect.colliderect(play_button):
            game_state = "playing"
            # Teleport player back to center so they don't spawn on the enemy
            player_box.rect.x = 400  
            player_box.rect.y = 300
            
        # If player walks into the EXIT button
        elif player_box.rect.colliderect(exit_button):
            running = False

    elif game_state == "playing":
        # The enemy and damage logic ONLY run when the game is active
        enemy_box.update(player_box.rect)
        damage.process_collision(player_box, enemy_box)

    # --- 3. THE RENDER SPLIT ---
    screen.fill(background_color)

    if game_state == "menu":
        # Draw the Play Button (Green)
        pygame.draw.rect(screen, (0, 255, 0), play_button)
        play_text = font.render("PLAY", True, (0, 0, 0))
        screen.blit(play_text, (play_button.x + 50, play_button.y + 20))
        
        # Draw the Exit Button (Red)
        pygame.draw.rect(screen, (255, 0, 0), exit_button)
        exit_text = font.render("EXIT", True, (0, 0, 0))
        screen.blit(exit_text, (exit_button.x + 50, exit_button.y + 20))
        
        # Draw the player on top of the menu so you can see yourself moving
        player_box.draw(screen)

    elif game_state == "playing":
        # Draw the actual game
        player_box.draw(screen)
        enemy_box.draw(screen)
    
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