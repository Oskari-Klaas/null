import pygame


def text_color_for(fill):
    """Return readable text color based on a background fill."""
    brightness = fill[0] * 0.299 + fill[1] * 0.587 + fill[2] * 0.114
    return (0, 0, 0) if brightness > 150 else (255, 255, 255)


def tier_for(name, simple_enemies, curse_names):
    """Return the tier name for an enemy choice."""
    if name is None:
        return "EMPTY"
    if name in simple_enemies:
        return "EASY"
    if name in curse_names:
        return "CURSE"
    return "HARD"


def tier_color_for(name, simple_enemies, curse_names):
    """Return the display color for an enemy tier."""
    if name is None:
        return (70, 70, 80)
    if name in simple_enemies:
        return (76, 214, 132)
    if name in curse_names:
        return (189, 96, 255)
    return (255, 86, 86)


def clamp(value, low, high):
    """Clamp a value between low and high."""
    return max(low, min(high, value))


def brighten(color, amount):
    """Brighten an RGB tuple by a fixed amount."""
    return tuple(clamp(channel + amount, 0, 255) for channel in color)


def scaled_rect(rect, scale):
    """Return a scaled copy of a rectangle centered on its original center."""
    width = int(rect.width * scale)
    height = int(rect.height * scale)
    return pygame.Rect(rect.centerx - width // 2, rect.centery - height // 2, width, height)
