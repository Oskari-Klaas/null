import pygame


def draw_centered_text(screen, text, text_font, color, rect):
    rendered = text_font.render(text, True, color)
    x = rect.centerx - rendered.get_width() // 2
    y = rect.centery - rendered.get_height() // 2
    screen.blit(rendered, (x, y))


def draw_wrapped_text(screen, text, text_font, color, rect, line_gap=4):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = word if current_line == "" else f"{current_line} {word}"
        if text_font.size(test_line)[0] <= rect.width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    y = rect.y
    for line in lines:
        rendered = text_font.render(line, True, color)
        screen.blit(rendered, (rect.x, y))
        y += rendered.get_height() + line_gap
        if y > rect.bottom:
            break


def draw_arena_background(screen, fill, screen_width, screen_height):
    screen.fill(fill)
    grid_color = (
        max(0, fill[0] - 10),
        max(0, fill[1] - 10),
        max(0, fill[2] - 10),
    )
    for x in range(0, screen_width, 40):
        pygame.draw.line(screen, grid_color, (x, 0), (x, screen_height))
    for y in range(0, screen_height, 40):
        pygame.draw.line(screen, grid_color, (0, y), (screen_width, y))
    pygame.draw.rect(screen, (10, 10, 14), (0, 0, screen_width, screen_height), 5)
