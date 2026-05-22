def process_collision(player, enemy):
    if not player.alive:
        return
    if enemy.name in ["Stoplight", "Warden"]:
        return
    if enemy.state == "active" and player.rect.colliderect(enemy.rect):
        player.die()
