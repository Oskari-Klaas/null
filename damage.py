"""Collision handling for player and enemy interactions."""

def process_collision(player, enemy):
    """Check if the player collides with a dangerous enemy and kill them."""
    # Ignore collisions when the player is already dead.
    if not player.alive:
        return

    # Certain enemy types do not instantly kill the player on contact.
    if enemy.name in ["Stoplight", "Warden"]:
        return

    # Only active enemies pose a collision threat.
    if enemy.state == "active" and player.rect.colliderect(enemy.rect):
        player.die()
