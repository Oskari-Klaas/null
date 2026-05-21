import time
import pygame
import sys
import random
import enemy
import player
import damage 

pygame.init()

screen_width = 800
screen_height = 600
background_color = (87, 82, 81)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Nullscape: Evolution")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 22)
menu_font = pygame.font.SysFont(None, 48)

# --- 1. GAME ENTITIES & VARIABLES ---
player_box = player.Player(400, 500)
enemies = []
collectibles = []  # NEW: List to hold our collectibles
game_state = "menu"
round_timer = 0
collectible_spawn_timer = 0  # NEW: Tracks the 10-second auto-spawn
running = True

# --- 2. MENU & CHOOSING UI BOXES ---
play_button = pygame.Rect(100, 250, 200, 80)
exit_button = pygame.Rect(500, 250, 200, 80)

enemy_names = ["Stalker", "Sentinel", "Frag"]
choices = [
    pygame.Rect(150, 250, 90, 90),
    pygame.Rect(355, 250, 90, 90),
    pygame.Rect(560, 250, 90, 90)
]

# --- 3. HELPER FUNCTIONS ---
def spawn_collectible():
    # Spawns a 20x20 box somewhere on the map (keeping it away from the UI text at the top)
    x = random.randint(50, 750)
    y = random.randint(100, 550)
    collectibles.append(pygame.Rect(x, y, 20, 20))

def start_new_round(name):
    global game_state, round_timer, enemies, player_box, collectibles, collectible_spawn_timer
    
    enemies.append(enemy.Enemy(400, 100, name)) 
    
    for e in enemies:
        e.exact_x, e.exact_y = random.randint(50, 750), random.randint(50, 150)
        e.state = "idle"
        e.timer = random.randint(0, 60)
        e.speed = 0
        
    player_box.rect.center = (400, 500)
    round_timer = 60 * 60  # 60 seconds
    
    # NEW: Reset collectibles for the new round
    collectibles.clear()
    spawn_collectible()  # Spawn the very first one
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
            player_box.rect.center = (400, 500)
        elif player_box.rect.colliderect(exit_button):
            running = False

    # ROOM 2: THE ENEMY SELECTOR
    elif game_state == "choosing":
        if player_box.alive:
            for i, box in enumerate(choices):
                if player_box.rect.colliderect(box):
                    start_new_round(enemy_names[i])

    # ROOM 3: THE ACTUAL GAME
    elif game_state == "playing":
        if player_box.alive:
            # Enemy Update
            for e in enemies:
                e.update(player_box.rect)
                damage.process_collision(player_box, e)
            
            # --- NEW: COLLECTIBLE LOGIC ---
            # 1. The 10-Second Auto Spawner (60 frames * 10 seconds = 600)
            collectible_spawn_timer += 1
            if collectible_spawn_timer >= 300:
                spawn_collectible()
                collectible_spawn_timer = 0
                
            # 2. Player Collision with Collectibles
            for c in collectibles[:]:  # We use [:] to make a copy of the list while looping so we don't crash when deleting items
                if player_box.rect.colliderect(c):
                    collectibles.remove(c)
                    round_timer -= 300  # Instantly removes 5 seconds from the clock (60 fps * 5)
                    spawn_collectible() # Instantly spawns a new one
            # ------------------------------

            # Game Timer Logic
            round_timer -= 1
            if round_timer <= 0:
                game_state = "choosing"
                player_box.rect.center = (400, 500)
        else:
            if keys[pygame.K_r]:
                player_box = player.Player(400, 500)
                enemies = []
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
        for i, box in enumerate(choices):
            pygame.draw.rect(screen, (255, 255, 255), box, 2)
            name_label = font.render(enemy_names[i], True, (255, 255, 255))
            screen.blit(name_label, (box.x + 5, box.y - 30))

    elif game_state == "playing":
        # Draw enemies
        for e in enemies:
            e.draw(screen)
            
        # NEW: Draw collectibles (Golden color)
        for c in collectibles:
            pygame.draw.rect(screen, (255, 215, 0), c)
        
        # Timer UI
        timer_txt = font.render(f"SURVIVE: {round_timer//60}s | Round: {len(enemies)}", True, (255, 255, 255))
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