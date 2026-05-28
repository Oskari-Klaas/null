import math
import random

import pygame

import enemy
import utils


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def clear(self):
        self.particles.clear()

    def spawn_particles(self, x, y, color, amount=16, speed=3.0, life=34, size=3, style="dot"):
        for _ in range(amount):
            angle = random.uniform(0, math.tau)
            velocity = random.uniform(0.6, speed)
            max_life = random.randint(max(8, life // 2), life)
            self.particles.append(
                {
                    "x": float(x),
                    "y": float(y),
                    "vx": math.cos(angle) * velocity,
                    "vy": math.sin(angle) * velocity,
                    "life": max_life,
                    "max_life": max_life,
                    "color": utils.brighten(color, random.randint(-14, 24)),
                    "size": random.randint(2, size),
                    "style": style,
                    "spin": random.uniform(-0.25, 0.25),
                    "angle": angle,
                    "damp": random.uniform(0.88, 0.97),
                    "gravity": random.uniform(-0.015, 0.045),
                }
            )

    def spawn_edge_particles(self, rect, color, amount=3, speed=1.8, life=22):
        for _ in range(amount):
            edge = random.randrange(4)
            if edge == 0:
                x, y = random.randint(rect.left, rect.right), rect.top
                angle = random.uniform(-math.pi, 0)
            elif edge == 1:
                x, y = random.randint(rect.left, rect.right), rect.bottom
                angle = random.uniform(0, math.pi)
            elif edge == 2:
                x, y = rect.left, random.randint(rect.top, rect.bottom)
                angle = random.uniform(math.pi / 2, math.pi * 1.5)
            else:
                x, y = rect.right, random.randint(rect.top, rect.bottom)
                angle = random.uniform(-math.pi / 2, math.pi / 2)

            velocity = random.uniform(0.35, speed)
            max_life = random.randint(max(8, life // 2), life)
            self.particles.append(
                {
                    "x": float(x),
                    "y": float(y),
                    "vx": math.cos(angle) * velocity,
                    "vy": math.sin(angle) * velocity,
                    "life": max_life,
                    "max_life": max_life,
                    "color": utils.brighten(color, random.randint(-20, 32)),
                    "size": random.randint(2, 4),
                    "style": random.choice(["spark", "dot"]),
                    "spin": random.uniform(-0.35, 0.35),
                    "angle": angle,
                    "damp": random.uniform(0.84, 0.93),
                    "gravity": random.uniform(-0.03, 0.02),
                }
            )

    def spawn_panic_ripples(self, x, y, color):
        for size in (16, 30, 48):
            self.particles.append(
                {
                    "x": float(x),
                    "y": float(y),
                    "vx": 0.0,
                    "vy": 0.0,
                    "life": 18 + size // 4,
                    "max_life": 18 + size // 4,
                    "color": color,
                    "size": size,
                    "style": "ring",
                    "spin": 0.0,
                    "angle": 0.0,
                    "damp": 1.0,
                    "gravity": 0.0,
                }
            )

    def spawn_motion_trail(self, rect, previous_center, color, amount=2, spark=False):
        current_center = rect.center
        dx = current_center[0] - previous_center[0]
        dy = current_center[1] - previous_center[1]
        distance = math.hypot(dx, dy)
        if distance < 0.7:
            return

        dir_x = dx / distance
        dir_y = dy / distance
        speed = min(5.5, 0.4 + distance * 0.26)
        origin_x = current_center[0] - dir_x * rect.width * 0.42
        origin_y = current_center[1] - dir_y * rect.height * 0.42

        for _ in range(amount):
            side = random.uniform(-rect.width * 0.32, rect.width * 0.32)
            x = origin_x + (-dir_y * side) + random.uniform(-3, 3)
            y = origin_y + (dir_x * side) + random.uniform(-3, 3)
            max_life = random.randint(12, 24)
            self.particles.append(
                {
                    "x": float(x),
                    "y": float(y),
                    "vx": -dir_x * random.uniform(0.5, speed) + random.uniform(-0.45, 0.45),
                    "vy": -dir_y * random.uniform(0.5, speed) + random.uniform(-0.45, 0.45),
                    "life": max_life,
                    "max_life": max_life,
                    "color": utils.brighten(color, random.randint(-42, 18)),
                    "size": random.randint(3, 7),
                    "style": "spark" if spark and random.random() < 0.38 else "trail",
                    "spin": random.uniform(-0.18, 0.18),
                    "angle": math.atan2(dy, dx) + math.pi + random.uniform(-0.45, 0.45),
                    "damp": random.uniform(0.80, 0.91),
                    "gravity": random.uniform(-0.02, 0.025),
                }
            )

    def spawn_enemy_motion_trail(self, enemy_obj, previous_center):
        distance = math.hypot(
            enemy_obj.rect.centerx - previous_center[0],
            enemy_obj.rect.centery - previous_center[1],
        )
        if distance < 0.7:
            return

        base_color = enemy.enemy_color(enemy_obj.name)
        if enemy_obj.name == "Stalker":
            self.spawn_motion_trail(enemy_obj.rect, previous_center, base_color, amount=4, spark=True)
        elif enemy_obj.name == "Drifter":
            self.spawn_motion_trail(enemy_obj.rect, previous_center, (95, 230, 255), amount=3, spark=True)
        elif enemy_obj.name == "Pulse":
            self.spawn_motion_trail(enemy_obj.rect, previous_center, (255, 245, 90), amount=3)
        elif enemy_obj.name == "Sentinel":
            self.spawn_motion_trail(enemy_obj.rect, previous_center, base_color, amount=2)
        elif enemy_obj.name == "Reaper" and distance > 80:
            self.spawn_particles(previous_center[0], previous_center[1], base_color, amount=16, speed=3.8, life=28, size=4, style="spark")
            self.spawn_panic_ripples(enemy_obj.rect.centerx, enemy_obj.rect.centery, base_color)
        else:
            self.spawn_motion_trail(enemy_obj.rect, previous_center, base_color, amount=2)

    def spawn_void_particles(self, void_enemy, active=False):
        amount = 4 if active else 3
        radius = 36 if active else 28
        for _ in range(amount):
            angle = random.uniform(0, math.tau)
            distance = random.uniform(14, radius)
            x = void_enemy.rect.centerx + math.cos(angle) * distance
            y = void_enemy.rect.centery + math.sin(angle) * distance
            max_life = random.randint(22, 42)
            inward_speed = random.uniform(0.04, 0.22 if active else 0.14)
            orbit_speed = random.uniform(0.45, 1.15 if active else 0.85)
            orbit_dir = random.choice([-1, 1])
            if random.random() < (0.45 if active else 0.28):
                inward_speed = random.uniform(0.45, 1.25 if active else 0.85)
                orbit_speed *= 0.45
            self.particles.append(
                {
                    "x": float(x),
                    "y": float(y),
                    "vx": -math.cos(angle) * inward_speed + (-math.sin(angle) * orbit_speed * orbit_dir),
                    "vy": -math.sin(angle) * inward_speed + (math.cos(angle) * orbit_speed * orbit_dir),
                    "life": max_life,
                    "max_life": max_life,
                    "color": random.choice([(4, 4, 7), (12, 10, 18), (25, 18, 34), (45, 32, 62)]),
                    "size": random.randint(2, 7 if active else 5),
                    "style": random.choice(["dot", "trail"]),
                    "spin": random.uniform(-0.12, 0.12),
                    "angle": angle + (math.pi / 2 * orbit_dir),
                    "damp": random.uniform(0.93, 0.98),
                    "gravity": 0.0,
                }
            )

    def update_particles(self):
        for particle in self.particles[:]:
            if particle.get("style") == "spark":
                particle["vx"] += random.uniform(-0.08, 0.08)
                particle["vy"] += random.uniform(-0.08, 0.08)
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            particle["vx"] *= particle.get("damp", 0.96)
            particle["vy"] = particle["vy"] * particle.get("damp", 0.96) + particle.get("gravity", 0.03)
            particle["angle"] += particle.get("spin", 0.0)
            particle["life"] -= 1
            if particle["life"] <= 0:
                self.particles.remove(particle)

    def draw_particles(self, screen):
        for particle in self.particles:
            alpha = max(0.0, min(1.0, particle["life"] / particle["max_life"]))
            x, y = int(particle["x"]), int(particle["y"])
            color = particle["color"]
            style = particle.get("style", "dot")

            if style == "spark":
                length = max(4, int(particle["size"] * 4 * alpha))
                dx = math.cos(particle["angle"]) * length
                dy = math.sin(particle["angle"]) * length
                pygame.draw.line(screen, color, (x, y), (int(x - dx), int(y - dy)), max(1, int(2 * alpha)))
            elif style == "trail":
                size = max(2, int(particle["size"] * alpha))
                trail_rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
                pygame.draw.rect(screen, color, trail_rect)
            elif style == "ring":
                radius = max(2, int(particle["size"] * (1.0 - alpha * 0.45)))
                pygame.draw.circle(screen, color, (x, y), radius, max(1, int(3 * alpha)))
            else:
                radius = max(1, int(particle["size"] * alpha))
                pygame.draw.circle(screen, color, (x, y), radius)
