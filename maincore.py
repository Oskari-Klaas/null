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
game_state = "menu"
play_button = pygame.Rect(100, 250, 200, 80)
exit_button = pygame.Rect(500, 250, 200, 80)

font = pygame.font.SysFont(None, 48)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()