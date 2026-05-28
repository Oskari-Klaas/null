import os

import pygame


class AudioManager:
    """Load and play game sound effects and music tracks."""

    def __init__(self, audio_directory, music_paths, volumes):
        self.audio_directory = audio_directory
        self.music_paths = music_paths
        self.volumes = volumes
        self.enabled = False
        self.current_music_track = None
        self.sound_effects = {}
        self.movement_sound_cooldown = 0

    def init(self):
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(22050, -16, 1, 512)
            except pygame.error:
                self.enabled = False
                return

        self.enabled = True
        pygame.mixer.set_num_channels(16)
        sound_paths = {
            "click": os.path.join(self.audio_directory, "ui_click.wav"),
            "select": os.path.join(self.audio_directory, "ui_select.wav"),
            "back": os.path.join(self.audio_directory, "ui_back.wav"),
            "coin": os.path.join(self.audio_directory, "coin_pickup.wav"),
            "move": os.path.join(self.audio_directory, "player_move.wav"),
            "win": os.path.join(self.audio_directory, "round_win.wav"),
            "death": os.path.join(self.audio_directory, "death_hit.wav"),
        }

        for name, path in sound_paths.items():
            if not os.path.exists(path):
                continue
            try:
                self.sound_effects[name] = pygame.mixer.Sound(path)
            except pygame.error:
                continue

        sound_volumes = {
            "click": 0.24,
            "select": 0.30,
            "back": 0.24,
            "coin": 0.50,
            "move": 0.18,
            "win": 0.54,
            "death": 0.72,
        }
        for name, volume in sound_volumes.items():
            if name in self.sound_effects:
                self.sound_effects[name].set_volume(volume)

    def play(self, name):
        if not self.enabled:
            return

        sound = self.sound_effects.get(name)
        if sound is not None:
            sound.play()

    def update_movement(self, player_obj):
        if self.movement_sound_cooldown > 0:
            self.movement_sound_cooldown -= 1

        if player_obj.moving and self.movement_sound_cooldown <= 0:
            self.play("move")
            self.movement_sound_cooldown = 14

    def reset_movement(self):
        self.movement_sound_cooldown = 0

    def switch_music(self, track):
        if not self.enabled or self.current_music_track == track:
            return

        path = self.music_paths.get(track)
        if path is None or not os.path.exists(path):
            return

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.volumes.get(track, 0.45))
            try:
                pygame.mixer.music.play(-1, fade_ms=650)
            except TypeError:
                pygame.mixer.music.play(-1)
            self.current_music_track = track
        except pygame.error:
            self.current_music_track = None
