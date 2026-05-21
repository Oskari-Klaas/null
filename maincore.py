import time
import pygame
import sys
import random
import math
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

# Fonts
font = pygame.font.SysFont("Arial", 22, bold=True)
menu_font = pygame.font.SysFont(None, 48)

# --- 1. GAME ENTITIES & VARIABLES ---
player_box = player.Player(400, 500)
enemies = []
collectibles = []  
game_state = "menu"
round_timer = 0
collectible_spawn_timer = 0  
running = True

# --- 2. MENU & CHOOSING UI BOXES ---
play_button = pygame.Rect(100, 250, 200, 80)
exit_button = pygame.Rect(500, 250, 200, 80)

# Friend's randomized enemy pool system
enemy_pool = ["Stalker", "Sentinel", "Ghost", "Pulse", "Reaper", "Void"]
current_choices = []
choices_rects = [
    pygame.Rect(125, 250, 100, 100), 
    pygame.Rect(350, 250, 100, 100), 
    pygame.Rect(575, 250, 100, 100)
]

def refresh_choices():
    global current_choices
    current_choices = random.sample(enemy_pool, 3)

refresh_choices() # Roll the dice for the first time

# --- 3. HELPER FUNCTIONS ---
def spawn_collectible():
    x = random.randint(50, 750)
    y = random.randint(100, 550)
    collectibles.append(pygame.Rect(x, y, 20, 20))

def start_new_round(name):
    global game_state, round_timer, enemies, player_box, collectibles, collectible_spawn_timer
    
    enemies.append(enemy.Enemy(400, 100, name)) 
    
    for e in enemies:
        # Friend's code: The Void enemy doesn't teleport around randomly at start
        if getattr(e, 'name', name) != "Void": 
            e.exact_x, e.exact_y = random.randint(100, 700), random.randint(50, 150)
        e.state = "idle"
        e.timer = random.randint(0, 30)
        e.speed = 0
        
    player_box.rect.center = (400, 500)
    round_timer = 60 * 60  # Friend's code: 60 seconds
    
    collectibles.clear()
    spawn_collectible() 
    collectible_spawn_timer = 0
    
    game_state = "playing"


# --- 4. THE MASTER APPLICATION LOOP ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # --- THE LOGIC FIREWALL ---
    if player_box.alive:
        player_box.move(keys)

    # ROOM 1: THE MENU
    if game_state == "menu":
        if player_box.rect.colliderect(play_button):
            game_state = "choosing"
            refresh_choices() # Reroll enemies when entering the room
            player_box.rect.center = (400, 500)
        elif player_box.rect.colliderect(exit_button):
            running = False

    # ROOM 2: THE ENEMY SELECTOR
    elif game_state == "choosing":
        if player_box.alive:
            for i, box in enumerate(choices_rects):
                if player_box.rect.colliderect(box):
                    start_new_round(current_choices[i])

    # ROOM 3: THE ACTUAL GAME
    elif game_state == "playing":
        if player_box.alive:
            
            # Enemy Update Loop (With friend's new Void gravity pull)
            for e in enemies:
                if getattr(e, 'name', '') == "Void":
                    dx = e.rect.centerx - player_box.rect.centerx
                    dy = e.rect.centery - player_box.rect.centery
                    dist = math.hypot(dx, dy)
                    if dist < 200: # If player is close, get sucked in
                        player_box.rect.x += int(dx * 0.03)
                        player_box.rect.y += int(dy * 0.03)

                e.update(player_box.rect)
                damage.process_collision(player_box, e)
            
            # Collectible Logic
            collectible_spawn_timer += 1
            if collectible_spawn_timer >= 300: # Auto-spawn every 5 seconds
                spawn_collectible()
                collectible_spawn_timer = 0
                
            for c in collectibles[:]: 
                if player_box.rect.colliderect(c):
                    collectibles.remove(c)
                    round_timer -= 300  
                    spawn_collectible() 
            
            # Game Timer Logic
            round_timer -= 1
            if round_timer <= 0:
                game_state = "choosing"
                refresh_choices() # Reroll the 3 bosses for the next round
                player_box.rect.center = (400, 500)
        else:
            if keys[pygame.K_r]:
                player_box = player.Player(400, 500)
                enemies = []
                refresh_choices()
                game_state = "choosing"

    # --- THE RENDER SPLIT ---
    screen.fill(background_color)

    if game_state == "menu":
        pygame.draw.rect(screen, (0, 255, 0), play_button)
        play_text = menu_font.render("PLAY", True, (0, 0, 0))
        screen.blit(play_text, (play_button.x + 50, play_button.y + 20))
        
        pygame.draw.rect(screen, (255, 0, 0), exit_button)
        exit_text = menu_font.render("EXIT", True, (0, 0, 0))
        screen.blit(exit_text, (exit_button.x + 50, exit_button.y + 20))

    elif game_state == "choosing":
        for i, box in enumerate(choices_rects):
            pygame.draw.rect(screen, (200, 200, 200), box, 3)
            name_label = font.render(current_choices[i], True, (255, 255, 255))
            screen.blit(name_label, (box.x + 5, box.y - 30))

    elif game_state == "playing":
        for e in enemies:
            e.draw(screen)
            
        for c in collectibles:
            pygame.draw.rect(screen, (255, 215, 0), c)
        
        timer_txt = font.render(f"TIME: {round_timer//60}s | ROUND: {len(enemies)}", True, (255, 255, 255))
        screen.blit(timer_txt, (15, 15))

    # Draw player
    if player_box.alive:
        player_box.draw(screen)
    elif not player_box.alive and game_state == "playing":
        msg = menu_font.render("DIED! PRESS 'R' TO RESTART", True, (255, 50, 50))
        screen.blit(msg, (150, 250)) 

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()