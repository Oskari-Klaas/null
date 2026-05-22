import pygame, sys, random, math, enemy, player, damage 

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Null")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)
menu_font = pygame.font.SysFont(None, 64)
big_font = pygame.font.SysFont(None, 100, bold=True)

player_box = player.Player(400, 500)
enemies, collectibles = [], []
game_state = "menu"
round_timer, round_number, collectible_spawn_timer = 0, 0, 0
freeze_timer, choice_cooldown = 0, 0
void_picked = stoplight_picked = False 
warden_queued = False 
warden_spawn_timer = 0 
running = True

BG_NORMAL, BG_WARNING, BG_DEATH = (87, 82, 81), (204, 183, 107), (180, 50, 50)
PLAY_COL, EXIT_COL = (0, 200, 0), (200, 0, 0)

play_button = pygame.Rect(100, 250, 200, 80)
exit_button = pygame.Rect(500, 250, 200, 80)
choices_rects = [pygame.Rect(125, 250, 100, 100), pygame.Rect(350, 250, 100, 100), pygame.Rect(575, 250, 100, 100)]
current_choices = []

def spawn_collectible():
    collectibles.append(pygame.Rect(random.randint(50, 750), random.randint(100, 550), 20, 20))

def refresh_choices():
    global current_choices
    weaker, stronger = ["Sentinel", "Glitch", "Magnet"], ["Stalker", "Pulse", "Reaper"]
    has_moving_enemy = any(e.name not in ["Void", "Stoplight", "Warden"] for e in enemies)
    
    if round_number <= 3: s_ch, sp_ch = 0.10, 0.15
    elif round_number <= 8: s_ch, sp_ch = 0.50, 0.35
    else: s_ch, sp_ch = 0.85, 0.55

    picked = []
    while len(picked) < 3:
        if has_moving_enemy and random.random() < sp_ch:
            specials = ["Warden"]
            if not void_picked: specials.append("Void")
            if not stoplight_picked: specials.append("Stoplight")
            choice = random.choice(specials)
        else:
            choice = random.choice(stronger if (random.random() < s_ch) else weaker)
        if choice not in picked: picked.append(choice)
    current_choices = picked

def reset_game_data():
    global enemies, round_number, void_picked, stoplight_picked, warden_queued, collectibles, collectible_spawn_timer
    enemies, collectibles = [], []
    round_number = 0
    void_picked = stoplight_picked = warden_queued = False
    collectible_spawn_timer = 0

def start_new_round(name):
    global game_state, round_timer, round_number, void_picked, stoplight_picked, warden_queued, warden_spawn_timer, freeze_timer, collectible_spawn_timer
    round_number += 1
    warden_queued = False
    if name == "Stoplight": stoplight_picked = True
    elif name == "Void": void_picked = True
    elif name == "Warden": warden_queued, warden_spawn_timer = True, random.randint(300, 900) 
    
    if name != "Warden": enemies.append(enemy.Enemy(400, 100, name)) 
    for e in enemies:
        if e.name not in ["Stoplight", "Warden"]:
            e.exact_x, e.exact_y = random.randint(100, 700), random.randint(50, 150)
            e.rect.topleft = (int(e.exact_x), int(e.exact_y))
        e.state, e.timer = "idle", 0
    
    player_box.pos_x, player_box.pos_y = 400.0, 500.0 
    player_box.rect.topleft = (400, 500)
    freeze_timer, round_timer = 90, 2100 
    collectibles.clear()
    spawn_collectible()
    game_state = "playing"

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
    
    keys = pygame.key.get_pressed()
    current_bg, show_stop, time_frozen = BG_NORMAL, False, False

    if freeze_timer > 0: freeze_timer -= 1
    if choice_cooldown > 0: choice_cooldown -= 1

    if game_state == "menu":
        player_box.move(keys)
        if player_box.rect.colliderect(play_button):
            reset_game_data()
            game_state, round_number = "choosing", 0
            refresh_choices(); freeze_timer, choice_cooldown = 90, 30
        elif player_box.rect.colliderect(exit_button): running = False

    elif game_state == "choosing":
        if freeze_timer == 0:
            player_box.move(keys)
            if choice_cooldown == 0:
                for i, box in enumerate(choices_rects):
                    if player_box.rect.colliderect(box): start_new_round(current_choices[i])

    elif game_state == "playing":
        if not player_box.alive:
            if keys[pygame.K_r]:
                reset_game_data(); player_box = player.Player(400, 500)
                game_state = "choosing"; refresh_choices(); freeze_timer, choice_cooldown = 90, 40
            if keys[pygame.K_m]:
                reset_game_data(); player_box = player.Player(400, 500); game_state = "menu"
        else:
            for e in enemies[:]:
                if e.name == "Warden" and not e.touched:
                    time_frozen = True
                    if player_box.rect.colliderect(e.rect):
                        e.touched = True; enemies.remove(e)

            if freeze_timer == 0:
                if warden_queued and not time_frozen:
                    warden_spawn_timer -= 1
                    if warden_spawn_timer <= 0:
                        f = max([(50,50),(750,50),(50,550),(750,550)], key=lambda c: math.hypot(c[0]-player_box.rect.x, c[1]-player_box.rect.y))
                        enemies.append(enemy.Enemy(f[0], f[1], "Warden")); warden_queued = False
                
                p_pull_x = p_pull_y = 0
                for e in enemies:
                    if e.name == "Stoplight":
                        if e.state == "warning": 
                            current_bg, show_stop = BG_WARNING, True
                            if player_box.rect.colliderect(e.rect):
                                e.stand_timer -= 1
                                if e.stand_timer <= 0: e.state, e.timer = "idle", 0 
                        elif e.state == "check": 
                            current_bg, show_stop = BG_DEATH, True
                            player_box.die()
                    elif e.name == "Void":
                        dx, dy = e.rect.centerx - player_box.rect.centerx, e.rect.centery - player_box.rect.centery
                        dist = math.hypot(dx, dy)
                        if 0 < dist < 220:
                            s = min(dist * 0.035, 4.5) * (1.0 + (round_number // 10) * 0.2)
                            p_pull_x += (dx/dist) * s; p_pull_y += (dy/dist) * s

                player_box.move(keys, p_pull_x, p_pull_y)
                for e in enemies:
                    e.update(player_box.rect, round_number, collectibles)
                    damage.process_collision(player_box, e)
                
                if not time_frozen:
                    round_timer -= 1
                    # COIN LOGIC: 5-second interval
                    collectible_spawn_timer += 1
                    if collectible_spawn_timer >= 300:
                        spawn_collectible(); collectible_spawn_timer = 0
                
                for c in collectibles[:]:
                    if player_box.rect.colliderect(c):
                        collectibles.remove(c)
                        round_timer -= 300
                        spawn_collectible() # COIN LOGIC: Immediate respawn

                if round_timer <= 0: 
                    player_box.pos_x, player_box.pos_y = 400.0, 500.0
                    player_box.rect.topleft = (400, 500)
                    game_state = "choosing"; refresh_choices(); freeze_timer, choice_cooldown = 90, 40

    # --- DRAWING ---
    screen.fill(current_bg)
    if game_state == "playing":
        for c in collectibles: pygame.draw.rect(screen, (255, 215, 0), c)
        for e in enemies:
            if e.name == "Stoplight" and e.state == "warning":
                pygame.draw.rect(screen, (255,255,255), (e.rect.x, e.rect.y-10, (e.stand_timer/30.0)*50, 5))
            e.draw(screen)

    player_box.draw(screen) 

    if game_state == "menu":
        pygame.draw.rect(screen, PLAY_COL, play_button)
        pygame.draw.rect(screen, EXIT_COL, exit_button)
        screen.blit(menu_font.render("PLAY", True, (255,255,255)), (play_button.x+40, play_button.y+15))
        screen.blit(menu_font.render("EXIT", True, (255,255,255)), (exit_button.x+45, exit_button.y+15))
    
    elif game_state == "choosing":
        for i, box in enumerate(choices_rects):
            pygame.draw.rect(screen, (50,50,50), box)
            pygame.draw.rect(screen, (200,200,200), box, 3)
            screen.blit(font.render(current_choices[i], True, (255,255,255)), (box.x, box.y-30))

    elif game_state == "playing":
        t_col = (255, 50, 50) if time_frozen else (100, 255, 100)
        screen.blit(font.render(f"TIME: {max(0, round_timer//60)}s | ROUND: {round_number}", True, t_col), (15,15))
        if show_stop:
            msg = "STAND ON IT!" if current_bg == BG_WARNING else "TOO LATE!"
            s_txt = big_font.render(msg, True, (255, 255, 255))
            screen.blit(s_txt, (400 - s_txt.get_width()//2, 120))

    if not player_box.alive and game_state == "playing":
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)); screen.blit(overlay, (0,0))
        d_txt = big_font.render("DIED!", True, (255,50,50))
        r_txt = menu_font.render("PRESS [R] RESTART    [M] MENU", True, (255,255,255))
        screen.blit(d_txt, (400 - d_txt.get_width()//2, 200))
        screen.blit(r_txt, (400 - r_txt.get_width()//2, 320))
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()