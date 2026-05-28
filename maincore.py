"""Main game module for the Null game.

This file initializes the game loop, audio, visuals, enemy spawning,
player input, and game state transitions.
"""

import math
import os
import random
import sys

import pygame
import damage
import enemy
import player

from audio_manager import AudioManager
from fade_transition import FadeTransition
from particles import ParticleSystem
from ui import draw_centered_text, draw_wrapped_text, draw_arena_background
from utils import (
    brighten,
    clamp,
    scaled_rect,
    text_color_for,
    tier_color_for,
    tier_for,
)


pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()
pygame.mixer.init()

screen_width = 800
screen_height = 600
background_color = (28, 28, 36)
warning_color = (190, 164, 74)
death_color = (150, 35, 42)

display_surface = pygame.display.set_mode((screen_width, screen_height))
screen = pygame.Surface((screen_width, screen_height))
pygame.display.set_caption("Null")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 22, bold=True)
small_font = pygame.font.SysFont("Arial", 16, bold=True)
menu_font = pygame.font.SysFont(None, 48)
big_font = pygame.font.SysFont(None, 100, bold=True)

base_dir = os.path.dirname(os.path.abspath(__file__))
audio_dir = os.path.join(base_dir, "assets", "audio")
music_files = {
    "menu": os.path.join(audio_dir, "menu_loop.wav"),
    "game": os.path.join(audio_dir, "game_loop.wav"),
    "hard": os.path.join(audio_dir, "hard_loop.wav"),
    "death": os.path.join(audio_dir, "death_muffled_loop.wav"),
}
music_volumes = {
    "menu": 0.52,
    "game": 0.58,
    "hard": 0.64,
    "death": 0.42,
}

audio_manager = AudioManager(audio_dir, music_files, music_volumes)
fade_transition_duration = 24
fade_transition = FadeTransition(fade_transition_duration)

player_box = player.Player(400, 500)
enemies = []
collectibles = []
game_state = "menu"
current_selection = "enemy"
round_timer = 0
round_number = 0
collectible_spawn_timer = 0
warden_queued = False
warden_spawn_timer = 0
debug_mode = False
menu_player_enabled = False
menu_click_timer = 0
menu_pop_timer = 0
menu_pop_duration = 26
info_click_timer = 0
death_shake_timer = 0
death_flash_timer = 0
panic_shake_timer = 0
frame_count = 0
selected_choice_index = None
selected_choice_name = None
choice_pop_timer = 0
choice_pop_duration = 28
round_intro_timer = 0
round_intro_duration = 92
round_intro_fade_duration = 48
selection_intro_timer = 0
selection_intro_duration = 18
menu_intro_timer = 0
menu_intro_duration = 42
survived_choice_active = False
survived_transition_target = None
main_menu_return_unlocked = True
survived_text_timer = 0
survived_text_duration = 38
survived_fade_timer = 0
survived_fade_duration = 14
pending_exit = False
running = True

play_button = pygame.Rect(100, 250, 200, 80)
exit_button = pygame.Rect(500, 250, 200, 80)
survived_menu_button = pygame.Rect(30, 520, 285, 48)

simple_enemies = ["Sentinel", "Drifter", "The Weaver"]
hard_enemies = ["Stalker", "Pulse", "Reaper"]
curse_names = ["Stoplight", "Warden", "Void"]
picked_curses = []
easy_choice_cooldowns = {}
recent_enemy_choices = []
easy_escape_streak = 0
force_hard_selection = False
forced_hard_cycles = 0
pressure_round_active = False
curse_unlock_round = 7
curse_interval = 3
buff_anchor_round = 5
buff_round_interval = 5
weaver_pressure_level = 0

current_choices = []
inspected_choice_index = None
particle_system = ParticleSystem()
choices_rects = [
    pygame.Rect(90, 240, 160, 130),
    pygame.Rect(320, 240, 160, 130),
    pygame.Rect(550, 240, 160, 130),
]

choice_descriptions = {
    "Sentinel": "Chases the player directly. Slow at first, faster after buffs.",
    "Drifter": "Moves straight up, down, left, or right. Its lane pulls you toward it if you stand on that line. Touching Drifter kills you.",
    "The Weaver": "Touching it kills you. Each Weaver pick tightens the web. Its thread can be cut through coins or enemies.",
    "Stalker": "Locks onto a direction, winds up, then dashes very fast.",
    "Pulse": "Chases the player while its body grows and shrinks.",
    "Reaper": "Marks a red zone, then teleports there after a short delay.",
    "Stoplight": "When warning starts, stand still long enough or die.",
    "Warden": "Freezes the timer until the player touches it.",
    "Void": "Pulls the player toward itself from a distance.",
}


def text_color_for(fill):
    brightness = fill[0] * 0.299 + fill[1] * 0.587 + fill[2] * 0.114
    return (0, 0, 0) if brightness > 150 else (255, 255, 255)


def tier_for(name):
    if name is None:
        return "EMPTY"
    if name in simple_enemies:
        return "EASY"
    if name in curse_names:
        return "CURSE"
    return "HARD"


def tier_color_for(name):
    if name is None:
        return (70, 70, 80)
    if name in simple_enemies:
        return (76, 214, 132)
    if name in curse_names:
        return (189, 96, 255)
    return (255, 86, 86)


def has_regular_enemy():
    """Check if any non-curse enemies are present in the current enemy list."""
    return any(e.name not in curse_names for e in enemies)


def hard_spawn_chance():
    """Return the current probability of selecting a hard enemy."""
    if round_number < 3:
        base_chance = 0.05
    else:
        base_chance = 0.60 + (round_number - 3) * 0.04
    return min(0.95, base_chance + forced_hard_cycles * 0.07)


def hard_chance_percent():
    if force_hard_selection or pressure_round_active:
        return 100
    return int(round(hard_spawn_chance() * 100))


def round_buff_level():
    return max(0, (round_number - buff_anchor_round) // buff_round_interval)


def round_buff_mult():
    return 1.0 + round_buff_level() * 0.18


def high_danger_choices_active():
    return round_number >= 5 and hard_spawn_chance() >= 0.60


def reduce_easy_cooldowns():
    for name in list(easy_choice_cooldowns):
        easy_choice_cooldowns[name] -= 1
        if easy_choice_cooldowns[name] <= 0:
            del easy_choice_cooldowns[name]


def blocked_enemy_choice():
    if len(recent_enemy_choices) >= 2 and recent_enemy_choices[-1] == recent_enemy_choices[-2]:
        return recent_enemy_choices[-1]
    return None


def remember_enemy_choice(name):
    recent_enemy_choices.append(name)
    del recent_enemy_choices[:-3]


def register_enemy_choice(name):
    global easy_escape_streak, force_hard_selection, forced_hard_cycles

    if name in simple_enemies and high_danger_choices_active():
        easy_escape_streak += 1
        if easy_escape_streak >= 2:
            force_hard_selection = True
            forced_hard_cycles += 1
            easy_escape_streak = 0
    elif name in hard_enemies:
        easy_escape_streak = 0
        force_hard_selection = False


def should_offer_curse_selection():
    next_round = round_number + 1
    return (
        has_regular_enemy()
        and len(picked_curses) < len(curse_names)
        and next_round >= curse_unlock_round
        and (next_round - curse_unlock_round) % curse_interval == 0
    )


def refresh_enemy_choices():
    """Pick the next set of enemy choices for the player selection screen."""
    global current_choices, current_selection, force_hard_selection, pressure_round_active
    global inspected_choice_index

    current_selection = "enemy"
    inspected_choice_index = None
    reduce_easy_cooldowns()

    if force_hard_selection:
        blocked_name = blocked_enemy_choice()
        hard_options = [name for name in hard_enemies if name != blocked_name]
        current_choices = random.sample(hard_options, min(3, len(hard_options)))
        while len(current_choices) < 3:
            current_choices.append(None)
        force_hard_selection = False
        pressure_round_active = True
        return

    pressure_round_active = False
    picked = []

    while len(picked) < 3:
        blocked_name = blocked_enemy_choice()
        simple_options = [
            name
            for name in simple_enemies
            if name not in picked and name not in easy_choice_cooldowns and name != blocked_name
        ]
        hard_options = [name for name in hard_enemies if name not in picked and name != blocked_name]
        wants_hard = random.random() < hard_spawn_chance()

        if wants_hard and hard_options:
            options = hard_options
        elif simple_options:
            options = simple_options
        else:
            options = hard_options

        picked.append(random.choice(options))

    current_choices = picked


def refresh_curse_choices(reset_empty=False):
    global current_choices, current_selection, inspected_choice_index

    current_selection = "curse"
    inspected_choice_index = None
    remaining = [name for name in curse_names if name not in picked_curses]

    if reset_empty and not remaining:
        picked_curses.clear()
        remaining = curse_names[:]

    current_choices = remaining[:3]
    while len(current_choices) < 3:
        current_choices.append(None)


def init_audio():
    """Initialize audio resources and sound effects."""
    audio_manager.init()


def play_sound(name):
    """Play a sound effect by name."""
    audio_manager.play(name)


def update_movement_sound():
    """Update player movement sound playback based on movement state."""
    audio_manager.update_movement(player_box)


def music_track_for_state():
    """Choose the current music track based on the game state."""
    if game_state == "playing":
        if not player_box.alive:
            return "death"
        if any(e.name in hard_enemies for e in enemies):
            return "hard"
        return "game"
    return "menu"


def switch_music(track):
    audio_manager.switch_music(track)


def update_audio():
    """Ensure current music matches the active game state."""
    switch_music(music_track_for_state())


def prepare_next_selection():
    """Advance the game to a new enemy/curse selection screen."""
    global game_state

    if force_hard_selection:
        refresh_enemy_choices()
    elif should_offer_curse_selection():
        refresh_curse_choices()
    else:
        refresh_enemy_choices()

    player_box.set_position(400, 500, center=True)
    game_state = "choosing"


def begin_fade_transition(state, target_state):
    global game_state, loading_timer, loading_duration, transition_switched, transition_target_state

    loading_duration = fade_transition_duration
    loading_timer = loading_duration
    transition_switched = False
    transition_target_state = target_state
    game_state = state


def complete_menu_start_transition():
    global menu_player_enabled

    reset_game_data()
    refresh_enemy_choices()
    player_box.alive = True
    player_box.color = (147, 112, 219)
    player_box.set_position(400, 500, center=True)
    menu_player_enabled = False


def complete_menu_return_transition():
    global menu_intro_timer, menu_player_enabled

    reset_game_data()
    player_box.alive = True
    player_box.color = (147, 112, 219)
    player_box.set_position(400, 500, center=True)
    menu_player_enabled = False
    menu_intro_timer = menu_intro_duration


def complete_fade_transition_step():
    global game_state, transition_switched

    state = game_state
    if state == "loading":
        complete_menu_start_transition()
    elif state == "selection_loading":
        finish_selection_loading()
    elif state == "menu_loading":
        complete_menu_return_transition()
    elif state == "round_loading":
        finish_round_transition()

    game_state = state
    transition_switched = True


def finish_fade_transition():
    global game_state, transition_switched, transition_target_state

    game_state = transition_target_state or game_state
    transition_target_state = None
    transition_switched = False


def fade_transition_alpha():
    if loading_duration <= 0:
        return 0

    progress = 1.0 - (loading_timer / loading_duration)
    progress = max(0.0, min(1.0, progress))
    if progress < 0.5:
        fade = progress * 2.0
    else:
        fade = (1.0 - progress) * 2.0
    return int(255 * max(0.0, min(1.0, fade)))


def visual_game_state():
    if game_state == "loading":
        return "choosing" if transition_switched else "menu"
    if game_state == "selection_loading":
        return "choosing" if transition_switched else "playing"
    if game_state == "menu_loading":
        return "menu" if transition_switched else "playing"
    if game_state == "round_loading":
        return "playing" if transition_switched else "choosing"
    return game_state


def begin_menu_start_transition():
    global game_state, menu_pop_timer

    play_sound("select")
    menu_pop_timer = menu_pop_duration
    game_state = "menu_confirm"
    particle_system.spawn_particles(play_button.centerx, play_button.centery, (100, 255, 170), amount=34, speed=5.0, style="spark")
    particle_system.spawn_panic_ripples(play_button.centerx, play_button.centery, (100, 255, 170))


def finish_menu_start_transition():
    begin_fade_transition("loading", "choosing")


def begin_selection_loading():
    begin_fade_transition("selection_loading", "choosing")


def finish_selection_loading():
    global game_state, selection_intro_timer, main_menu_return_unlocked

    prepare_next_selection()
    main_menu_return_unlocked = True
    selection_intro_timer = selection_intro_duration
    game_state = "selection_intro"


def begin_menu_return_loading():
    begin_fade_transition("menu_loading", "menu")


def begin_survived_transition():
    global survived_choice_active, survived_transition_target, survived_text_timer, survived_fade_timer

    survived_choice_active = True
    survived_transition_target = "selection"
    survived_text_timer = survived_text_duration
    survived_fade_timer = 0
    particle_system.spawn_particles(player_box.rect.centerx, player_box.rect.centery, (170, 255, 190), amount=44, speed=4.4, life=42, size=5, style="spark")
    particle_system.spawn_panic_ripples(player_box.rect.centerx, player_box.rect.centery, (170, 255, 190))


def begin_selection_menu_return():
    global game_state, survived_transition_target, survived_fade_timer, survived_text_timer
    global main_menu_return_unlocked

    play_sound("back")
    main_menu_return_unlocked = False
    survived_transition_target = "menu"
    survived_text_timer = 0
    survived_fade_timer = survived_fade_duration
    game_state = "selection_menu_fade"
    particle_system.spawn_particles(survived_menu_button.centerx, survived_menu_button.centery, (170, 210, 255), amount=24, speed=2.6, life=34, style="dot")


def begin_round_transition(choice_index):
    global game_state, selected_choice_index, selected_choice_name, choice_pop_timer
    global inspected_choice_index

    if choice_index < 0 or choice_index >= len(current_choices):
        return

    choice_name = current_choices[choice_index]
    if choice_name is None:
        return

    selected_choice_index = choice_index
    selected_choice_name = choice_name
    inspected_choice_index = None
    play_sound("select")
    choice_pop_timer = choice_pop_duration
    game_state = "choice_confirm"

    card = choices_rects[choice_index]
    particle_system.spawn_particles(card.centerx, card.centery, tier_color_for(choice_name), amount=30, speed=4.4, life=32, size=4, style="spark")
    particle_system.spawn_panic_ripples(card.centerx, card.centery, tier_color_for(choice_name))


def finish_round_transition():
    global selected_choice_index, selected_choice_name, round_intro_timer

    if selected_choice_name is None:
        prepare_next_selection()
        return

    choice_name = selected_choice_name
    selected_choice_index = None
    selected_choice_name = None
    start_new_round(choice_name)
    round_intro_timer = max(0, round_intro_duration - round_intro_fade_duration)


def spawn_collectible():
    x = random.randint(50, 750)
    y = random.randint(100, 550)
    collectibles.append(pygame.Rect(x, y, 20, 20))


def spawn_warden():
    corners = [(30, 30), (720, 30), (30, 520), (720, 520)]
    farthest = max(
        corners,
        key=lambda pos: math.hypot(pos[0] - player_box.rect.x, pos[1] - player_box.rect.y),
    )
    enemies.append(enemy.Enemy(farthest[0], farthest[1], "Warden"))


def random_void_position():
    min_distance = 260
    best_pos = (400, 90)
    best_distance = 0

    for _ in range(35):
        x = random.randint(70, screen_width - 110)
        y = random.randint(70, screen_height - 160)
        distance = math.hypot(x + 20 - player_box.rect.centerx, y + 20 - player_box.rect.centery)
        if distance > best_distance:
            best_pos = (x, y)
            best_distance = distance
        if distance >= min_distance:
            return (x, y)

    return best_pos


def move_void_to_safe_spot(void_enemy):
    x, y = random_void_position()
    void_enemy.exact_x = float(x)
    void_enemy.exact_y = float(y)
    void_enemy.rect.topleft = (int(void_enemy.exact_x), int(void_enemy.exact_y))


def thread_hits_rect(start, end, rect):
    inflated = rect.inflate(8, 8)
    return bool(inflated.clipline(start, end))


def cut_weaver_thread(weaver):
    weaver.link_active = False
    weaver.thread_tense = False
    weaver.tension_timer = 0
    weaver.timer = 0


def weaver_enemies():
    return [e for e in enemies if e.name == "The Weaver"]


def weaver_shared_center(weavers):
    if not weavers:
        return (0, 0)
    center_x = sum(e.rect.centerx for e in weavers) / len(weavers)
    center_y = sum(e.rect.centery for e in weavers) / len(weavers)
    return (int(center_x), int(center_y))


def weaver_pressure_for_count(count):
    return max(weaver_pressure_level, count)


def weaver_shared_radius(buff_level, count, pressure_level=0):
    pressure = max(pressure_level, count)
    return max(165, 620 - buff_level * 85 - max(0, pressure - 1) * 52 - max(0, count - 1) * 14)


def weaver_tension_limit(buff_level, count, pressure_level=0):
    pressure = max(pressure_level, count)
    return max(55, 112 - buff_level * 12 - max(0, pressure - 1) * 12 - max(0, count - 1) * 4)


def weaver_start_timer():
    pressure = max(0, weaver_pressure_level - 1)
    head_start = min(150, pressure * 45)
    return random.randint(head_start, head_start + 30)


def apply_sentinel_spacing():
    sentinels = [e for e in enemies if e.name == "Sentinel"]
    if len(sentinels) < 2:
        return

    min_distance = 64
    for i, first in enumerate(sentinels):
        for j, second in enumerate(sentinels[i + 1 :], start=i + 1):
            dx = second.rect.centerx - first.rect.centerx
            dy = second.rect.centery - first.rect.centery
            distance = math.hypot(dx, dy)

            if distance == 0:
                angle = (i * 1.7 + j * 2.3 + frame_count * 0.05) % math.tau
                dx = math.cos(angle)
                dy = math.sin(angle)
                distance = 1

            if distance >= min_distance:
                continue

            push = (min_distance - distance) * 0.5
            push_x = (dx / distance) * push
            push_y = (dy / distance) * push

            first.exact_x = clamp(first.exact_x - push_x, 0, screen_width - first.rect.width)
            first.exact_y = clamp(first.exact_y - push_y, 0, screen_height - first.rect.height)
            second.exact_x = clamp(second.exact_x + push_x, 0, screen_width - second.rect.width)
            second.exact_y = clamp(second.exact_y + push_y, 0, screen_height - second.rect.height)
            first.rect.topleft = (int(first.exact_x), int(first.exact_y))
            second.rect.topleft = (int(second.exact_x), int(second.exact_y))


def reset_game_data():
    global enemies, collectibles, round_number, round_timer, collectible_spawn_timer
    global warden_queued, warden_spawn_timer, easy_escape_streak, force_hard_selection
    global forced_hard_cycles
    global pressure_round_active, death_shake_timer, death_flash_timer, panic_shake_timer
    global selected_choice_index, selected_choice_name, choice_pop_timer
    global round_intro_timer, selection_intro_timer, menu_intro_timer
    global survived_choice_active, survived_transition_target, survived_text_timer, survived_fade_timer
    global main_menu_return_unlocked
    global menu_pop_timer
    global weaver_pressure_level
    global movement_sound_cooldown

    enemies = []
    collectibles = []
    particle_system.clear()
    picked_curses.clear()
    easy_choice_cooldowns.clear()
    recent_enemy_choices.clear()
    round_number = 0
    round_timer = 0
    collectible_spawn_timer = 0
    warden_queued = False
    warden_spawn_timer = 0
    easy_escape_streak = 0
    force_hard_selection = False
    forced_hard_cycles = 0
    pressure_round_active = False
    weaver_pressure_level = 0
    death_shake_timer = 0
    death_flash_timer = 0
    panic_shake_timer = 0
    selected_choice_index = None
    selected_choice_name = None
    choice_pop_timer = 0
    round_intro_timer = 0
    selection_intro_timer = 0
    menu_intro_timer = 0
    survived_choice_active = False
    survived_transition_target = None
    main_menu_return_unlocked = True
    survived_text_timer = 0
    survived_fade_timer = 0
    menu_pop_timer = 0
    movement_sound_cooldown = 0


def start_new_round(name):
    """Initialize the next round and spawn the chosen enemy."""
    global game_state, round_timer, round_number, collectible_spawn_timer
    global warden_queued, warden_spawn_timer
    global weaver_pressure_level

    if name is None:
        return

    if name not in curse_names and name == blocked_enemy_choice():
        return

    if name not in curse_names:
        register_enemy_choice(name)
        remember_enemy_choice(name)

    round_number += 1

    if name in curse_names and name not in picked_curses:
        picked_curses.append(name)

    if name == "The Weaver":
        weaver_pressure_level += 1

    if name == "Warden":
        warden_queued = True
        buff_mult = round_buff_mult()
        min_spawn = max(120, int(300 / buff_mult))
        max_spawn = max(min_spawn + 90, int(900 / buff_mult))
        warden_spawn_timer = random.randint(min_spawn, max_spawn)
    elif name == "Void":
        x, y = random_void_position()
        enemies.append(enemy.Enemy(x, y, name))
    else:
        enemies.append(enemy.Enemy(400, 100, name))

    for e in enemies:
        if e.name not in ["Void", "Stoplight", "Warden"]:
            e.exact_x = float(random.randint(100, 700))
            e.exact_y = float(random.randint(50, 150))
            e.rect.topleft = (int(e.exact_x), int(e.exact_y))
        elif e.name == "Stoplight":
            e.rect.center = (400, 140)
            e.exact_x = float(e.rect.x)
            e.exact_y = float(e.rect.y)
        elif e.name == "Void":
            move_void_to_safe_spot(e)

        e.state = "idle"
        e.timer = weaver_start_timer() if e.name == "The Weaver" else random.randint(0, 30)
        e.speed = 0
        e.dir_x = 0
        e.dir_y = 0
        e.lane_axis = random.choice(["x", "y"])
        e.target_pos = e.rect.center
        e.link_active = False
        e.thread_tense = False
        e.tension_timer = 0
        e.show_warning = False
        e.stand_timer = 0
        e.touched = False

    player_box.set_position(400, 500, center=True)
    round_timer = 60 * 60
    collectible_spawn_timer = 0

    collectibles.clear()
    spawn_collectible()

    game_state = "playing"


def revive_player():
    player_box.alive = True
    player_box.color = (147, 112, 219)
    player_box.set_position(400, 500, center=True)


def handle_debug_key(key):
    global debug_mode, game_state, round_timer, warden_queued, warden_spawn_timer

    if key == pygame.K_F1:
        debug_mode = not debug_mode
        return

    if not debug_mode:
        return

    if key == pygame.K_F2:
        refresh_enemy_choices()
        player_box.set_position(400, 500, center=True)
        game_state = "choosing"
    elif key == pygame.K_F3:
        refresh_curse_choices(reset_empty=True)
        player_box.set_position(400, 500, center=True)
        game_state = "choosing"
    elif key == pygame.K_F4:
        start_new_round(random.choice(simple_enemies + hard_enemies))
    elif key == pygame.K_F5:
        if game_state == "playing":
            round_timer = 0
        else:
            prepare_next_selection()
    elif key == pygame.K_F6:
        enemies.clear()
        collectibles.clear()
        warden_queued = False
        warden_spawn_timer = 0
        spawn_collectible()
    elif key == pygame.K_F7:
        revive_player()


def trigger_death_effect():
    global death_shake_timer, death_flash_timer, panic_shake_timer

    play_sound("death")
    death_shake_timer = 42
    panic_shake_timer = 58
    death_flash_timer = 22
    particle_system.spawn_panic_ripples(player_box.rect.centerx, player_box.rect.centery, (255, 45, 70))
    particle_system.spawn_particles(
        player_box.rect.centerx,
        player_box.rect.centery,
        (255, 55, 80),
        amount=82,
        speed=9.0,
        life=58,
        size=6,
        style="spark",
    )
    particle_system.spawn_particles(
        player_box.rect.centerx,
        player_box.rect.centery,
        (245, 245, 255),
        amount=26,
        speed=5.5,
        life=32,
        size=3,
        style="dot",
    )


def kill_player():
    if player_box.alive:
        player_box.die()
        trigger_death_effect()


def draw_button(rect, fill, label, hovered=False, pressed=False, pop_progress=0.0):
    pulse = math.sin(frame_count * 0.42) if hovered else 0
    scale = 1.08 + pulse * 0.012 if hovered else 1.0
    if pressed:
        scale = 0.94
    if pop_progress > 0:
        scale = max(scale, 1.0 + math.sin(pop_progress * math.pi) * 0.22)
    draw_rect = scaled_rect(rect, scale)
    jitter_x = random.choice([-1, 0, 1]) if hovered and frame_count % 5 == 0 else 0
    lift = -4 if hovered else 0
    if pressed:
        lift = 3
    draw_rect.x += jitter_x
    draw_rect.y += lift

    button_fill = fill
    if hovered:
        button_fill = (
            min(255, fill[0] + 28),
            min(255, fill[1] + 28),
            min(255, fill[2] + 28),
        )
        if frame_count % 3 == 0:
            particle_system.spawn_edge_particles(draw_rect, button_fill, amount=2, speed=2.5, life=18)
    if pop_progress > 0 and frame_count % 2 == 0:
        particle_system.spawn_edge_particles(draw_rect, brighten(fill, 36), amount=4, speed=3.0, life=18)

    shadow = draw_rect.move(6, 8 if hovered else 6)
    pygame.draw.rect(screen, (8, 8, 12), shadow)
    pygame.draw.rect(screen, button_fill, draw_rect)
    pygame.draw.rect(screen, (255, 255, 255), draw_rect, 3)
    if hovered:
        pulse_size = 8 + int(abs(pulse) * 8)
        pygame.draw.rect(screen, (255, 255, 255), draw_rect.inflate(pulse_size, pulse_size), 2)
        for _ in range(2):
            slash_y = random.randint(draw_rect.top - 6, draw_rect.bottom + 6)
            slash_x = random.randint(draw_rect.left - 10, draw_rect.right - 10)
            pygame.draw.line(
                screen,
                brighten(button_fill, 45),
                (slash_x, slash_y),
                (slash_x + random.randint(10, 28), slash_y + random.choice([-2, -1, 1, 2])),
                1,
            )
    text_rect = draw_rect.move(random.choice([-1, 0, 1]) if hovered else 0, random.choice([-1, 0, 1]) if hovered else 0)
    draw_centered_text(screen, label, menu_font, text_color_for(button_fill), text_rect)


def choice_info_button_rect(card_rect):
    return pygame.Rect(card_rect.right - 28, card_rect.y + 31, 22, 22)


def choice_info_panel_rect():
    return pygame.Rect(110, 398, 580, 98)


def choice_info_close_rect():
    panel = choice_info_panel_rect()
    return pygame.Rect(panel.right - 32, panel.y + 10, 20, 20)


def draw_choice_icon(icon, name, fill, tier_fill):
    pygame.draw.rect(screen, (12, 12, 16), icon)
    pygame.draw.rect(screen, (245, 245, 255), icon, 2)
    cx, cy = icon.center

    if name == "Sentinel":
        pygame.draw.circle(screen, (18, 38, 44), (cx, cy), 14)
        pygame.draw.circle(screen, tier_fill, (cx, cy), 12, 3)
        pygame.draw.circle(screen, (245, 255, 255), (cx, cy), 5)
        pygame.draw.line(screen, tier_fill, (icon.left + 5, cy), (icon.right - 5, cy), 2)
    elif name == "Drifter":
        pygame.draw.line(screen, tier_fill, (cx, icon.top + 7), (cx, icon.bottom - 7), 4)
        pygame.draw.line(screen, tier_fill, (icon.left + 7, cy), (icon.right - 7, cy), 4)
        pygame.draw.polygon(screen, (245, 255, 255), [(cx, icon.top + 4), (cx - 5, icon.top + 13), (cx + 5, icon.top + 13)])
        pygame.draw.polygon(screen, (245, 255, 255), [(icon.right - 4, cy), (icon.right - 13, cy - 5), (icon.right - 13, cy + 5)])
    elif name == "The Weaver":
        points = [
            (cx, icon.top + 5),
            (icon.right - 6, cy),
            (cx, icon.bottom - 5),
            (icon.left + 6, cy),
        ]
        for point in points:
            pygame.draw.line(screen, tier_fill, (cx, cy), point, 2)
        pygame.draw.circle(screen, (230, 215, 255), (cx, cy), 11, 2)
        pygame.draw.circle(screen, tier_fill, (cx, cy), 5)
    elif name == "Stalker":
        pygame.draw.polygon(screen, (42, 8, 12), [(cx, icon.top + 5), (icon.right - 7, icon.bottom - 7), (icon.left + 7, icon.bottom - 7)])
        pygame.draw.polygon(screen, tier_fill, [(cx, icon.top + 9), (icon.right - 12, icon.bottom - 10), (icon.left + 12, icon.bottom - 10)], 2)
        pygame.draw.line(screen, (255, 230, 230), (cx, cy - 4), (cx, cy + 9), 2)
    elif name == "Pulse":
        pygame.draw.circle(screen, (55, 48, 8), (cx, cy), 14)
        pygame.draw.circle(screen, tier_fill, (cx, cy), 14, 2)
        pygame.draw.circle(screen, (255, 255, 210), (cx, cy), 8, 2)
        pygame.draw.circle(screen, tier_fill, (cx, cy), 3)
    elif name == "Reaper":
        pygame.draw.circle(screen, (34, 15, 48), (cx, cy), 14)
        pygame.draw.arc(screen, tier_fill, icon.inflate(-8, -6), math.radians(38), math.radians(318), 4)
        pygame.draw.line(screen, (235, 220, 255), (cx - 7, cy + 9), (cx + 11, cy - 9), 3)
    elif name == "Stoplight":
        body = icon.inflate(-14, -4)
        pygame.draw.rect(screen, (45, 12, 12), body)
        pygame.draw.circle(screen, (255, 60, 60), (cx, icon.top + 11), 5)
        pygame.draw.circle(screen, (255, 210, 60), (cx, cy), 5)
        pygame.draw.circle(screen, (80, 255, 110), (cx, icon.bottom - 11), 5)
    elif name == "Warden":
        shield = [(cx, icon.top + 5), (icon.right - 7, cy - 3), (icon.right - 11, icon.bottom - 8), (cx, icon.bottom - 4), (icon.left + 11, icon.bottom - 8), (icon.left + 7, cy - 3)]
        pygame.draw.polygon(screen, (48, 28, 12), shield)
        pygame.draw.polygon(screen, (255, 210, 115), shield, 2)
        pygame.draw.rect(screen, (255, 210, 115), (cx - 5, cy - 1, 10, 10), 2)
        pygame.draw.arc(screen, (255, 210, 115), (cx - 7, cy - 11, 14, 14), math.pi, math.tau, 2)
    elif name == "Void":
        pygame.draw.circle(screen, (2, 2, 4), (cx, cy), 15)
        pygame.draw.circle(screen, (95, 60, 145), (cx, cy), 14, 2)
        pygame.draw.arc(screen, (190, 120, 255), icon.inflate(-8, -8), 0.3, 4.8, 3)
        pygame.draw.circle(screen, (20, 20, 24), (cx, cy), 5)
    else:
        inner_icon = icon.inflate(-10, -10)
        pygame.draw.rect(screen, fill, inner_icon)
        pygame.draw.rect(screen, (12, 12, 16), inner_icon, 2)


def draw_choice_card(rect, name, inspected=False, hovered=False, selected=False, confirming=False):
    active = hovered or selected or inspected
    tier = tier_for(name)
    if confirming:
        progress = 1.0 - (choice_pop_timer / max(1, choice_pop_duration))
        progress = max(0.0, min(1.0, progress))
        pop_scale = 1.0 + math.sin(progress * math.pi) * 0.20
        rect = scaled_rect(rect, pop_scale)
        active = True
        if frame_count % 2 == 0:
            particle_system.spawn_edge_particles(rect, tier_color_for(name), amount=4, speed=3.0, life=18)

    if active:
        if tier == "EASY":
            rect = rect.move(
                int(math.sin(frame_count * 0.13) * 1.4),
                int(math.cos(frame_count * 0.10) * 1.0),
            )
            if frame_count % 10 == 0:
                particle_system.spawn_edge_particles(rect, tier_color_for(name), amount=1, speed=0.9, life=30)
        elif tier in ["HARD", "CURSE"]:
            rect = rect.move(
                random.choice([-2, -1, 0, 1, 2]) if frame_count % 3 == 0 else 0,
                random.choice([-2, -1, 0, 1, 2]) if frame_count % 4 == 0 else 0,
            )
            if frame_count % 3 == 0:
                particle_system.spawn_edge_particles(rect, tier_color_for(name), amount=3 if hovered else 2, speed=2.4, life=18)
        else:
            rect = rect.move(
                random.choice([-1, 0, 1]) if frame_count % 6 == 0 else 0,
                random.choice([-1, 0, 1]) if frame_count % 7 == 0 else 0,
            )

    if name is None:
        shadow = rect.move(7, 7)
        pygame.draw.rect(screen, (8, 8, 12), shadow)
        pygame.draw.rect(screen, (34, 34, 42), rect)
        pygame.draw.rect(screen, (255, 225, 95) if inspected else (80, 80, 92), rect, 3)
        if active:
            pygame.draw.rect(screen, (210, 210, 235), rect.inflate(8, 8), 1)
        tier_rect = pygame.Rect(rect.x, rect.y, rect.width, 26)
        pygame.draw.rect(screen, tier_color_for(name), tier_rect)
        draw_centered_text(screen, "EMPTY", small_font, (210, 210, 220), tier_rect)
        draw_centered_text(screen, "-", big_font, (110, 110, 126), rect)
        return

    fill = enemy.enemy_color(name)
    tier_fill = tier_color_for(name)
    label_color = text_color_for(fill)

    shadow = rect.move(7, 7)
    pygame.draw.rect(screen, (8, 8, 12), shadow)
    pygame.draw.rect(screen, fill, rect)
    pygame.draw.rect(screen, (255, 225, 95) if inspected else (255, 255, 255), rect, 3)
    if active:
        if tier == "EASY":
            pulse = 4 + int(abs(math.sin(frame_count * 0.14)) * 4)
            calm_color = brighten(tier_fill, 30)
            pygame.draw.rect(screen, calm_color, rect.inflate(pulse, pulse), 1)
            pygame.draw.rect(screen, (210, 255, 225), rect.inflate(pulse + 5, pulse + 5), 1)
        else:
            pulse = 6 + int(abs(math.sin(frame_count * 0.25)) * 9)
            pygame.draw.rect(screen, tier_fill, rect.inflate(pulse, pulse), 2)
            pygame.draw.line(
                screen,
                brighten(tier_fill, 45),
                (rect.left - 8, rect.top + random.randint(16, rect.height - 16)),
                (rect.right + 8, rect.top + random.randint(16, rect.height - 16)),
                1,
            )

    tier_rect = pygame.Rect(rect.x, rect.y, rect.width, 26)
    pygame.draw.rect(screen, tier_fill, tier_rect)
    pygame.draw.line(screen, (255, 255, 255), tier_rect.bottomleft, tier_rect.bottomright, 2)
    draw_centered_text(screen, tier_for(name), small_font, text_color_for(tier_fill), tier_rect)

    icon = pygame.Rect(rect.centerx - 21, rect.y + 41, 42, 42)
    draw_choice_icon(icon, name, fill, tier_fill)

    name_rect = pygame.Rect(rect.x + 6, rect.y + 88, rect.width - 12, 34)
    draw_centered_text(screen, name, font, label_color, name_rect)

    info_rect = choice_info_button_rect(rect)
    if inspected and info_click_timer > 0:
        pulse = info_click_timer // 2
        pygame.draw.rect(screen, (255, 225, 95), info_rect.inflate(pulse * 2, pulse * 2), 2)
    pygame.draw.rect(screen, (12, 12, 16), info_rect)
    pygame.draw.rect(screen, (255, 255, 255), info_rect, 2)
    draw_centered_text(screen, "?", small_font, (255, 255, 255), info_rect)


def draw_choice_info_panel(name):
    if name is None:
        return

    panel = choice_info_panel_rect()
    if info_click_timer > 0:
        panel = panel.inflate(info_click_timer, info_click_timer // 2)
    pygame.draw.rect(screen, (14, 14, 20), panel)
    pygame.draw.rect(screen, tier_color_for(name), panel, 3)

    close_rect = pygame.Rect(panel.right - 32, panel.y + 10, 20, 20)
    pygame.draw.rect(screen, (35, 35, 46), close_rect)
    pygame.draw.rect(screen, (255, 255, 255), close_rect, 2)
    draw_centered_text(screen, "X", small_font, (255, 255, 255), close_rect)

    title_rect = pygame.Rect(panel.x + 18, panel.y + 12, panel.width - 58, 24)
    title_text = f"{name} | {tier_for(name)}"
    screen.blit(font.render(title_text, True, (240, 240, 255)), title_rect.topleft)

    desc_rect = pygame.Rect(panel.x + 18, panel.y + 45, panel.width - 36, 42)
    draw_wrapped_text(
        choice_descriptions.get(name, "No data available yet."),
        small_font,
        (190, 200, 230),
        desc_rect,
    )


def draw_choosing_screen(confirming_index=None):
    if current_selection == "curse":
        title_text = "CHOOSE A CURSE"
    elif round_number == 0:
        title_text = "CHOOSE YOUR THREAT"
    else:
        title_text = "CHOOSE YOUR NEXT THREAT"
    title = menu_font.render(title_text, True, (235, 235, 255))
    screen.blit(title, (400 - title.get_width() // 2, 135))

    round_label = "ROUND: 0" if round_number == 0 else f"NEXT ROUND: {round_number + 1}"
    next_round_text = small_font.render(round_label, True, (210, 220, 255))
    screen.blit(next_round_text, (400 - next_round_text.get_width() // 2, 112))

    if current_selection == "curse":
        info_text = f"CURSES LEFT: {len(curse_names) - len(picked_curses)}"
    else:
        locked_easy = ", ".join(
            f"{name}:{turns}" for name, turns in sorted(easy_choice_cooldowns.items())
        )
        if pressure_round_active:
            info_text = "HARD CHANCE: 100% | PRESSURE ROUND"
        elif locked_easy:
            info_text = f"HARD CHANCE: {hard_chance_percent()}% | EASY LOCK: {locked_easy}"
        else:
            info_text = f"HARD CHANCE: {hard_chance_percent()}%"
    info_label = small_font.render(info_text, True, (170, 185, 220))
    screen.blit(info_label, (400 - info_label.get_width() // 2, 185))

    for i, box in enumerate(choices_rects):
        card_hovered = box.collidepoint(mouse_pos)
        card_selected = player_box.rect.colliderect(box)
        draw_choice_card(
            box,
            current_choices[i],
            inspected_choice_index == i,
            card_hovered,
            card_selected,
            confirming_index == i,
        )

    if inspected_choice_index is not None and confirming_index is None:
        draw_choice_info_panel(current_choices[inspected_choice_index])

    if confirming_index is None:
        draw_survived_button(survived_menu_button, "Back to Main menu?", anxious=False)


def draw_survived_button(rect, label, anxious=False):
    hovered = rect.collidepoint(mouse_pos)
    draw_rect = rect.copy()

    if anxious:
        anxiety = min(1.0, round_number / 10.0)
        shake = 1 + int(anxiety * 8)
        if hovered or frame_count % max(2, 7 - min(5, round_number // 2)) == 0:
            draw_rect.x += random.randint(-shake, shake)
            draw_rect.y += random.randint(-max(1, shake // 2), max(1, shake // 2))
        fill = (120 + int(anxiety * 65), 24, 34)
        border = (255, 80 + int(anxiety * 80), 95)
        if frame_count % max(2, 8 - min(5, round_number // 3)) == 0:
            particle_system.spawn_edge_particles(draw_rect, border, amount=2 + int(anxiety * 3), speed=1.8 + anxiety * 2.4, life=18)
    else:
        sway_x = int(math.sin(frame_count * 0.08) * 2)
        sway_y = int(math.cos(frame_count * 0.07) * 1)
        draw_rect = draw_rect.move(sway_x, sway_y)
        fill = (30, 48, 78)
        border = (150, 190, 255)
        if hovered and frame_count % 8 == 0:
            particle_system.spawn_edge_particles(draw_rect, border, amount=1, speed=0.9, life=28)

    if hovered:
        draw_rect = draw_rect.inflate(8, 4)
        fill = brighten(fill, 24)

    shadow = draw_rect.move(5, 6)
    pygame.draw.rect(screen, (4, 5, 8), shadow)
    pygame.draw.rect(screen, fill, draw_rect)
    pygame.draw.rect(screen, border, draw_rect, 2 if not anxious else 3)
    if anxious:
        pygame.draw.line(
            screen,
            brighten(border, 36),
            (draw_rect.left - 6, draw_rect.centery + random.randint(-12, 12)),
            (draw_rect.right + 6, draw_rect.centery + random.randint(-12, 12)),
            1,
        )
    else:
        pygame.draw.rect(screen, (210, 230, 255), draw_rect.inflate(6, 6), 1)

    draw_centered_text(screen, label, small_font, (255, 255, 255), draw_rect)


def draw_survived_overlay():
    if not survived_choice_active and survived_fade_timer <= 0:
        return

    if survived_fade_timer > 0 and survived_text_timer <= 0:
        fade_progress = 1.0 - (survived_fade_timer / max(1, survived_fade_duration))
        fade = pygame.Surface((800, 600), pygame.SRCALPHA)
        fade.fill((0, 0, 0, int(255 * max(0.0, min(1.0, fade_progress)))))
        screen.blit(fade, (0, 0))

    alpha = 255
    if survived_text_timer > survived_text_duration - 20:
        alpha = int(255 * ((survived_text_duration - survived_text_timer) / 20))
    elif survived_fade_timer > 0:
        alpha = int(255 * (survived_fade_timer / max(1, survived_fade_duration)))

    survived_txt = menu_font.render("YOU SURVIVED", True, (220, 255, 225))
    survived_txt.set_alpha(max(0, min(255, alpha)))
    text_x = 400 - survived_txt.get_width() // 2 + random.choice([-1, 0, 1])
    text_y = 225 + random.choice([-1, 0, 1])
    screen.blit(survived_txt, (text_x, text_y))

    visible_timer = survived_text_timer if survived_text_timer > 0 else frame_count
    if visible_timer % 8 == 0:
        particle_system.spawn_edge_particles(pygame.Rect(260, 214, 280, 62), (170, 255, 190), amount=2, speed=1.6, life=24)


refresh_enemy_choices()
init_audio()
update_audio()

# Main game loop: process input, update logic, render each frame.
while running:
    frame_count += 1
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            handle_debug_key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_state == "menu":
            if play_button.collidepoint(event.pos):
                menu_click_timer = 10
                begin_menu_start_transition()
            elif exit_button.collidepoint(event.pos):
                play_sound("back")
                menu_click_timer = 10
                particle_system.spawn_particles(exit_button.centerx, exit_button.centery, (255, 95, 105), amount=34, speed=5.0, style="spark")
                pending_exit = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_state == "choosing":
            if inspected_choice_index is not None and choice_info_close_rect().collidepoint(event.pos):
                inspected_choice_index = None
                info_click_timer = 8
                play_sound("back")
                continue

            clicked_info_button = False
            for i, box in enumerate(choices_rects):
                if choice_info_button_rect(box).collidepoint(event.pos) and current_choices[i] is not None:
                    inspected_choice_index = None if inspected_choice_index == i else i
                    info_click_timer = 12
                    play_sound("click")
                    particle_system.spawn_particles(event.pos[0], event.pos[1], (255, 225, 95), amount=18, speed=3.4, life=24, style="spark")
                    clicked_info_button = True
                    break

            if inspected_choice_index is not None and not clicked_info_button:
                if not choice_info_panel_rect().collidepoint(event.pos):
                    inspected_choice_index = None

    particle_system.update_particles()
    if menu_click_timer > 0:
        menu_click_timer -= 1
    if menu_pop_timer > 0:
        menu_pop_timer -= 1
    if pending_exit and menu_click_timer == 0:
        running = False
    if info_click_timer > 0:
        info_click_timer -= 1
    if death_shake_timer > 0:
        death_shake_timer -= 1
    if panic_shake_timer > 0:
        panic_shake_timer -= 1
    if death_flash_timer > 0:
        death_flash_timer -= 1

    keys = pygame.key.get_pressed()
    current_bg = background_color
    show_stop = False
    time_frozen = False
    holding_still = not (
        keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]
    )
    move_x = keys[pygame.K_d] - keys[pygame.K_a]
    move_y = keys[pygame.K_s] - keys[pygame.K_w]

    if game_state == "menu":
        pass

    elif game_state == "menu_confirm":
        if menu_pop_timer <= 0:
            finish_menu_start_transition()

    elif game_state in ["loading", "selection_loading", "menu_loading", "round_loading"]:
        loading_timer -= 1
        if not transition_switched and loading_timer <= loading_duration // 2:
            complete_fade_transition_step()
        if loading_timer <= 0:
            finish_fade_transition()

    elif game_state == "selection_intro":
        if selection_intro_timer > 0:
            selection_intro_timer -= 1
        else:
            game_state = "choosing"

    elif game_state == "selection_menu_fade":
        if survived_fade_timer > 0:
            survived_fade_timer -= 1
        else:
            complete_menu_return_transition()
            game_state = "menu_intro"

    elif game_state == "menu_intro":
        if menu_intro_timer > 0:
            menu_intro_timer -= 1
        else:
            game_state = "menu"

    elif game_state == "choosing":
        previous_player_center = player_box.rect.center
        player_box.move(keys)
        update_movement_sound()
        particle_system.spawn_motion_trail(player_box.rect, previous_player_center, player_box.color, amount=2)
        if player_box.rect.colliderect(survived_menu_button):
            begin_selection_menu_return()
        for i, box in enumerate(choices_rects):
            if player_box.rect.colliderect(box) and current_choices[i] is not None:
                begin_round_transition(i)
                break

    elif game_state == "choice_confirm":
        if choice_pop_timer > 0:
            choice_pop_timer -= 1
        else:
            begin_fade_transition("round_loading", "playing")

    elif game_state == "playing":
        if not player_box.alive:
            if keys[pygame.K_r]:
                play_sound("select")
                reset_game_data()
                player_box = player.Player(400, 500)
                refresh_enemy_choices()
                game_state = "choosing"
            elif keys[pygame.K_m]:
                play_sound("back")
                begin_menu_return_loading()
        elif round_intro_timer > 0:
            round_intro_timer -= 1
        elif survived_choice_active:
            if survived_text_timer > 0:
                survived_text_timer -= 1
                if survived_text_timer <= 0:
                    survived_fade_timer = survived_fade_duration
            elif survived_fade_timer > 0:
                survived_fade_timer -= 1
                if survived_fade_timer <= 0:
                    survived_choice_active = False
                    finish_selection_loading()
        else:
            was_alive = player_box.alive
            pull_x = 0
            pull_y = 0
            buff_level = round_buff_level()
            buff_mult = round_buff_mult()
            weavers = weaver_enemies()
            weaver_count = len(weavers)
            weaver_pressure = weaver_pressure_for_count(weaver_count)
            active_weaver_count = max(1, sum(1 for w in weavers if getattr(w, "link_active", False)))
            shared_weaver_center = weaver_shared_center(weavers)
            shared_weaver_radius = weaver_shared_radius(buff_level, weaver_count, weaver_pressure)
            shared_weaver_tension_limit = weaver_tension_limit(buff_level, weaver_count, weaver_pressure)

            for e in enemies[:]:
                if e.name == "Warden" and not e.touched:
                    if player_box.rect.colliderect(e.rect):
                        e.touched = True
                        enemies.remove(e)
                    else:
                        time_frozen = True

            if warden_queued and not time_frozen:
                warden_spawn_timer -= 1
                if warden_spawn_timer <= 0:
                    spawn_warden()
                    warden_queued = False

            for e in enemies:
                if e.name == "Stoplight":
                    if e.state == "warning":
                        current_bg = warning_color
                        show_stop = True
                        if holding_still:
                            e.stand_timer += 1
                            if e.stand_timer >= 42:
                                e.state = "idle"
                                e.timer = 0
                                e.stand_timer = 0
                        else:
                            e.stand_timer = 0
                    elif e.state == "check":
                        current_bg = death_color
                        show_stop = True
                        kill_player()
                elif e.name == "Void":
                    dx = e.rect.centerx - player_box.rect.centerx
                    dy = e.rect.centery - player_box.rect.centery
                    dist = math.hypot(dx, dy)
                    pull_radius = 170 + buff_level * 24
                    if frame_count % 4 == 0:
                        particle_system.spawn_void_particles(e, dist < pull_radius)
                    if 0 < dist < pull_radius:
                        pull_strength = 0.020 + buff_level * 0.004
                        pull_cap = 2.9 + buff_level * 0.55
                        pull = min(dist * pull_strength * buff_mult, pull_cap)
                        pull_x += (dx / dist) * pull
                        pull_y += (dy / dist) * pull
                elif e.name == "Drifter":
                    if e.dir_x != 0 or e.dir_y != 0:
                        lane_pull = 1.35 + buff_level * 0.18
                        if e.lane_axis == "x":
                            toward_drifter = e.rect.centerx - player_box.rect.centerx
                            touching_line = player_box.rect.top <= e.rect.centery <= player_box.rect.bottom
                            if touching_line and toward_drifter != 0:
                                pull_x += (toward_drifter / abs(toward_drifter)) * lane_pull
                        else:
                            toward_drifter = e.rect.centery - player_box.rect.centery
                            touching_line = player_box.rect.left <= e.rect.centerx <= player_box.rect.right
                            if touching_line and toward_drifter != 0:
                                pull_y += (toward_drifter / abs(toward_drifter)) * lane_pull
                elif e.name == "The Weaver" and e.link_active:
                    start = e.rect.center
                    end = player_box.rect.center
                    thread_cut = any(thread_hits_rect(start, end, coin) for coin in collectibles)

                    if not thread_cut:
                        for other in enemies:
                            if other is not e and thread_hits_rect(start, end, other.rect):
                                thread_cut = True
                                break

                    if thread_cut:
                        cut_weaver_thread(e)
                    else:
                        e.thread_radius = shared_weaver_radius
                        dx = shared_weaver_center[0] - player_box.rect.centerx
                        dy = shared_weaver_center[1] - player_box.rect.centery
                        dist = math.hypot(dx, dy)
                        e.thread_tense = dist > shared_weaver_radius

                        if dist > 0 and e.thread_tense:
                            toward_x = dx / dist
                            toward_y = dy / dist
                            moving_toward_weaver = (move_x * toward_x + move_y * toward_y) > 0.2
                            tension_limit = shared_weaver_tension_limit
                            e.tension_limit = tension_limit
                            shared_weaver_bonus = max(0, weaver_pressure - 1)
                            pull_bonus = 1.0 + shared_weaver_bonus * 0.16
                            pull_share = pull_bonus / active_weaver_count
                            pull_strength = min(
                                (5.5 + buff_level * 0.65) * pull_share,
                                (1.4 + buff_level * 0.25 + (dist - shared_weaver_radius) * 0.045) * pull_share,
                            )
                            pull_x += toward_x * pull_strength
                            pull_y += toward_y * pull_strength

                            if moving_toward_weaver:
                                e.tension_timer = max(0, e.tension_timer - 3)
                            else:
                                e.tension_timer += 1
                                if shared_weaver_bonus > 0 and frame_count % 2 == 0:
                                    e.tension_timer += 1

                            if e.tension_timer >= tension_limit:
                                away_x = -toward_x
                                away_y = -toward_y
                                player_box.set_position(
                                    int(player_box.rect.x + away_x * 110),
                                    int(player_box.rect.y + away_y * 110),
                                )
                                kill_player()
                        else:
                            e.thread_tense = False
                            e.tension_timer = 0
            previous_player_center = player_box.rect.center
            player_box.move(keys, pull_x, pull_y)
            update_movement_sound()
            particle_system.spawn_motion_trail(player_box.rect, previous_player_center, player_box.color, amount=3, spark=True)

            for e in enemies:
                previous_enemy_center = e.rect.center
                e.update(player_box.rect, round_number, collectibles)
                particle_system.spawn_enemy_motion_trail(e, previous_enemy_center)

            apply_sentinel_spacing()

            for e in enemies:
                damage.process_collision(player_box, e)

            if was_alive and not player_box.alive and death_shake_timer == 0:
                trigger_death_effect()

            if not time_frozen:
                round_timer -= 1
                collectible_spawn_timer += 1
                if collectible_spawn_timer >= 300:
                    spawn_collectible()
                    collectible_spawn_timer = 0

            for c in collectibles[:]:
                if player_box.rect.colliderect(c):
                    if not time_frozen:
                        collectibles.remove(c)
                        play_sound("coin")
                        round_timer -= 300
                        spawn_collectible()
                    elif frame_count % 8 == 0:
                        particle_system.spawn_edge_particles(c.inflate(8, 8), (255, 95, 95), amount=1, speed=1.0, life=16)

            if round_timer <= 0:
                begin_survived_transition()

    update_audio()
    render_state = visual_game_state()

    draw_arena_background(screen, current_bg, screen_width, screen_height)

    # Main render pass for the current frame.
    if render_state in ["menu", "menu_confirm", "menu_intro"]:
        title = big_font.render("NULL", True, (230, 230, 255))
        screen.blit(title, (400 - title.get_width() // 2, 105))
        subtitle = font.render("2D CURSE RUN", True, (150, 180, 255))
        screen.blit(subtitle, (400 - subtitle.get_width() // 2, 190))
        play_hovered = play_button.collidepoint(mouse_pos)
        exit_hovered = exit_button.collidepoint(mouse_pos)
        play_pop_progress = 1.0 - (menu_pop_timer / max(1, menu_pop_duration)) if menu_pop_timer > 0 else 0.0
        play_pressed = (menu_click_timer > 0 and play_hovered) or game_state == "menu_confirm"
        exit_pressed = menu_click_timer > 0 and exit_hovered
        draw_button(play_button, (0, 220, 120), "PLAY", play_hovered, play_pressed, play_pop_progress)
        draw_button(exit_button, (220, 55, 65), "EXIT", exit_hovered, exit_pressed)

        hint = small_font.render("CLICK PLAY TO ENTER SELECTION", True, (175, 190, 230))
        screen.blit(hint, (400 - hint.get_width() // 2, 355))

    elif render_state in ["choosing", "choice_confirm", "selection_intro", "selection_menu_fade"]:
        selected_for_draw = selected_choice_index if game_state in ["choice_confirm", "round_loading"] else None
        draw_choosing_screen(selected_for_draw)

    elif render_state == "playing":
        visible_weavers = weaver_enemies()
        if visible_weavers:
            ring_buff_level = round_buff_level()
            ring_weaver_count = len(visible_weavers)
            ring_weaver_pressure = weaver_pressure_for_count(ring_weaver_count)
            ring_center = weaver_shared_center(visible_weavers)
            ring_radius = weaver_shared_radius(ring_buff_level, ring_weaver_count, ring_weaver_pressure)
            ring_color = (255, 45, 65) if any(getattr(e, "thread_tense", False) for e in visible_weavers) else (70, 35, 115)
            ring_width = 2 if ring_weaver_count > 1 else 1
            pygame.draw.circle(screen, ring_color, ring_center, ring_radius, ring_width)
            if ring_weaver_count > 1:
                pygame.draw.circle(screen, (190, 95, 255), ring_center, 7)

        for e in enemies:
            if e.name == "Stoplight" and e.state == "warning":
                bar_rect = pygame.Rect(300, 224, 200, 12)
                bar_width = int((e.stand_timer / 42.0) * bar_rect.width)
                pygame.draw.rect(screen, (12, 12, 16), bar_rect)
                pygame.draw.rect(screen, (255, 255, 255), (bar_rect.x, bar_rect.y, bar_width, bar_rect.height))
                pygame.draw.rect(screen, (255, 255, 255), bar_rect, 2)
            e.draw(screen)

        for e in enemies:
            if e.name == "The Weaver" and e.link_active:
                color = (255, 45, 65) if e.thread_tense else (190, 95, 255)
                width = 4 if e.thread_tense else 2
                start = e.rect.center
                end = player_box.rect.center
                if e.thread_tense:
                    for _ in range(2):
                        offset = (random.randint(-2, 2), random.randint(-2, 2))
                        pygame.draw.line(
                            screen,
                            brighten(color, random.randint(-8, 28)),
                            (start[0] + offset[0], start[1] + offset[1]),
                            (end[0] - offset[0], end[1] - offset[1]),
                            width,
                        )
                    if frame_count % 5 == 0:
                        point = random.random()
                        spark_x = start[0] + (end[0] - start[0]) * point
                        spark_y = start[1] + (end[1] - start[1]) * point
                        particle_system.spawn_particles(spark_x, spark_y, color, amount=2, speed=1.8, life=16, size=3, style="spark")
                else:
                    pygame.draw.line(screen, color, start, end, width)
                if e.thread_tense:
                    tension_limit = max(
                        1,
                        weaver_tension_limit(
                            round_buff_level(),
                            len(visible_weavers),
                            weaver_pressure_for_count(len(visible_weavers)),
                        ),
                    )
                    timer_width = int((e.tension_timer / tension_limit) * 70)
                    pygame.draw.rect(screen, (12, 12, 16), (e.rect.centerx - 35, e.rect.y - 16, 70, 7))
                    pygame.draw.rect(screen, color, (e.rect.centerx - 35, e.rect.y - 16, timer_width, 7))

        for c in collectibles:
            pygame.draw.circle(screen, (255, 225, 70), c.center, 11)
            pygame.draw.circle(screen, (120, 80, 10), c.center, 11, 2)

        hud_rect = pygame.Rect(10, 10, 360, 38)
        pygame.draw.rect(screen, (12, 12, 18), hud_rect)
        pygame.draw.rect(screen, (90, 100, 130), hud_rect, 2)
        timer_color = (255, 75, 75) if time_frozen else (210, 255, 210)
        timer_txt = font.render(
            f"TIME: {max(0, round_timer // 60)}s | ROUND: {round_number} | BUFF +{round_buff_level()}",
            True,
            timer_color,
        )
        screen.blit(timer_txt, (22, 18))

        curse_txt = small_font.render(
            f"CURSES: {len(picked_curses)}/{len(curse_names)}",
            True,
            (205, 170, 255),
        )
        curse_rect = pygame.Rect(670, 10, 120, 30)
        pygame.draw.rect(screen, (12, 12, 18), curse_rect)
        pygame.draw.rect(screen, (125, 85, 165), curse_rect, 2)
        screen.blit(curse_txt, (curse_rect.centerx - curse_txt.get_width() // 2, 18))

        if time_frozen:
            freeze_txt = font.render("TIME LOCKED", True, (255, 95, 95))
            freeze_jitter = random.choice([-2, -1, 0, 1, 2]) if frame_count % 3 == 0 else 0
            screen.blit(freeze_txt, (400 - freeze_txt.get_width() // 2 + freeze_jitter, 65))
            if frame_count % 6 == 0:
                particle_system.spawn_edge_particles(player_box.rect.inflate(18, 18), (255, 80, 100), amount=2, speed=1.7, life=20)

        if show_stop:
            msg = "STAY STILL!" if current_bg == warning_color else "TOO LATE!"
            stop_txt = big_font.render(msg, True, (255, 255, 255))
            stop_x = 400 - stop_txt.get_width() // 2 + random.choice([-3, -1, 0, 1, 3])
            stop_y = 120 + random.choice([-2, 0, 2])
            screen.blit(stop_txt, (stop_x, stop_y))
            if frame_count % 4 == 0:
                warning_rect = pygame.Rect(265, 105, 270, 76)
                particle_system.spawn_edge_particles(warning_rect, (255, 245, 215), amount=3, speed=2.6, life=18)

    particle_system.draw_particles(screen)

    if render_state in ["choosing", "choice_confirm", "selection_intro", "selection_menu_fade", "playing"] or menu_player_enabled:
        player_box.draw(screen)

    if debug_mode:
        debug_rect = pygame.Rect(560, 48, 225, 32)
        pygame.draw.rect(screen, (12, 12, 18), debug_rect)
        pygame.draw.rect(screen, (255, 210, 80), debug_rect, 2)
        debug_txt = small_font.render(
            f"DEBUG | {game_state.upper()} | {current_selection.upper()}",
            True,
            (255, 230, 130),
        )
        screen.blit(debug_txt, (debug_rect.x + 9, debug_rect.y + 8))

    if game_state == "selection_intro":
        fade_progress = selection_intro_timer / max(1, selection_intro_duration)
        fade = pygame.Surface((800, 600), pygame.SRCALPHA)
        fade.fill((0, 0, 0, int(255 * max(0.0, min(1.0, fade_progress)))))
        screen.blit(fade, (0, 0))

    if game_state == "selection_menu_fade":
        fade_progress = 1.0 - (survived_fade_timer / max(1, survived_fade_duration))
        fade = pygame.Surface((800, 600), pygame.SRCALPHA)
        fade.fill((0, 0, 0, int(255 * max(0.0, min(1.0, fade_progress)))))
        screen.blit(fade, (0, 0))

    if game_state == "menu_intro":
        fade_progress = menu_intro_timer / max(1, menu_intro_duration)
        fade = pygame.Surface((800, 600), pygame.SRCALPHA)
        fade.fill((0, 0, 0, int(255 * max(0.0, min(1.0, fade_progress)))))
        screen.blit(fade, (0, 0))

    if game_state in ["loading", "selection_loading", "round_loading", "menu_loading"]:
        fade = pygame.Surface((800, 600), pygame.SRCALPHA)
        fade.fill((0, 0, 0, fade_transition_alpha()))
        screen.blit(fade, (0, 0))

    if game_state == "playing" and player_box.alive and round_intro_timer > 0:
        elapsed = round_intro_duration - round_intro_timer
        intro = pygame.Surface((800, 600), pygame.SRCALPHA)
        if elapsed < round_intro_fade_duration:
            alpha = int(255 * (1.0 - elapsed / round_intro_fade_duration))
            intro.fill((0, 0, 0, alpha))
            screen.blit(intro, (0, 0))

        if 12 < elapsed < round_intro_duration - 10:
            ready_alpha = 255
            if elapsed < 28:
                ready_alpha = int(255 * ((elapsed - 12) / 16))
            elif round_intro_timer < 24:
                ready_alpha = int(255 * (round_intro_timer / 24))
            ready_txt = big_font.render("READY?", True, (255, 255, 255))
            ready_txt.set_alpha(max(0, min(255, ready_alpha)))
            ready_x = 400 - ready_txt.get_width() // 2 + random.choice([-1, 0, 1])
            ready_y = 210 + random.choice([-1, 0, 1])
            screen.blit(ready_txt, (ready_x, ready_y))

    if game_state == "playing" and player_box.alive:
        draw_survived_overlay()

    if not player_box.alive and game_state == "playing":
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        if death_flash_timer > 0:
            flash = pygame.Surface((800, 600), pygame.SRCALPHA)
            flash.fill((255, 45, 70, death_flash_timer * 10))
            screen.blit(flash, (0, 0))

        particle_system.draw_particles(screen)

        died_txt = big_font.render("DIED!", True, (255, 60, 70))
        restart_txt = menu_font.render("PRESS [R] RESTART    [M] MENU", True, (255, 255, 255))
        screen.blit(died_txt, (400 - died_txt.get_width() // 2, 200))
        screen.blit(restart_txt, (400 - restart_txt.get_width() // 2, 320))

    display_surface.fill((0, 0, 0))
    shake_x = shake_y = 0
    danger_strength = 0.0
    if game_state == "playing" and player_box.alive:
        if show_stop:
            danger_strength = max(danger_strength, 0.20 if current_bg == warning_color else 0.32)
        if time_frozen:
            danger_strength = max(danger_strength, 0.12)
        if any(e.name == "The Weaver" and getattr(e, "thread_tense", False) for e in enemies):
            danger_strength = max(danger_strength, 0.18)

    panic_strength = max(death_shake_timer / 42.0, panic_shake_timer / 58.0, danger_strength)
    if panic_strength > 0:
        shake_power = int(2 + 15 * panic_strength * panic_strength)
        stutter = -1 if frame_count % 2 == 0 else 1
        shake_x = int(math.sin(frame_count * 1.9) * shake_power * 0.65)
        shake_y = int(math.cos(frame_count * 2.6) * shake_power * 0.45)
        shake_x += random.randint(-shake_power, shake_power) + stutter * max(1, shake_power // 2)
        shake_y += random.randint(-shake_power, shake_power)

        if panic_shake_timer > 0 and frame_count % 3 != 0:
            ghost = screen.copy()
            ghost.set_alpha(int(44 * panic_strength))
            display_surface.blit(
                ghost,
                (
                    shake_x + random.choice([-7, -4, 4, 7]),
                    shake_y + random.choice([-3, 3]),
                ),
            )

    if panic_strength > 0:
        zoom = 1.0 + panic_strength * 0.018
        zoomed_size = (int(screen_width * zoom), int(screen_height * zoom))
        zoomed = pygame.transform.smoothscale(screen, zoomed_size)
        display_surface.blit(
            zoomed,
            (
                shake_x - (zoomed_size[0] - screen_width) // 2,
                shake_y - (zoomed_size[1] - screen_height) // 2,
            ),
        )
    else:
        display_surface.blit(screen, (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
