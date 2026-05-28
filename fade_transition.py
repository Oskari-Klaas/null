class FadeTransition:
    """Manage fade animation progress between game states."""

    states = {"loading", "selection_loading", "menu_loading", "round_loading"}

    def __init__(self, duration):
        self.duration = duration
        self.timer = 0
        self.switched = False
        self.target_state = None

    def begin(self, target_state):
        self.timer = self.duration
        self.switched = False
        self.target_state = target_state

    def tick(self):
        self.timer -= 1

    def should_switch(self):
        return not self.switched and self.timer <= self.duration // 2

    def mark_switched(self):
        self.switched = True

    def finished(self):
        return self.timer <= 0

    def finish(self, fallback_state):
        target = self.target_state or fallback_state
        self.target_state = None
        self.switched = False
        return target

    def alpha(self):
        if self.duration <= 0:
            return 0

        progress = 1.0 - (self.timer / self.duration)
        progress = max(0.0, min(1.0, progress))
        fade = progress * 2.0 if progress < 0.5 else (1.0 - progress) * 2.0
        return int(255 * max(0.0, min(1.0, fade)))

    def visual_state(self, state):
        if state == "loading":
            return "choosing" if self.switched else "menu"
        if state == "selection_loading":
            return "choosing" if self.switched else "playing"
        if state == "menu_loading":
            return "menu" if self.switched else "playing"
        if state == "round_loading":
            return "playing" if self.switched else "choosing"
        return state
