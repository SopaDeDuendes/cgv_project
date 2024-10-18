class Person:
    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.safe_zone_reached = False

    def move_towards_safe_zone(self, safe_zone_position):
        """Mueve la persona hacia la zona segura."""
        safe_x, safe_y = safe_zone_position
        if abs(self.x - safe_x) > 0.01:
            self.x += 0.01 if self.x < safe_x else -0.01
        if abs(self.y - safe_y) > 0.01:
            self.y += 0.01 if self.y < safe_y else -0.01

        # Si la persona ha alcanzado la zona segura
        if abs(self.x - safe_x) <= 0.01 and abs(self.y - safe_y) <= 0.01:
            self.safe_zone_reached = True

    def move_towards_stair(self, stair_position):
        """Mueve la persona hacia la escalera."""
        stair_x, stair_y = stair_position
        if abs(self.x - stair_x) > 0.01:
            self.x += 0.01 if self.x < stair_x else -0.01
        if abs(self.y - stair_y) > 0.01:
            self.y += 0.01 if self.y < stair_y else -0.01

    def reached_stair(self, stair_position):
        """Verifica si la persona ha llegado a la escalera."""
        stair_x, stair_y = stair_position
        return abs(self.x - stair_x) <= 0.05 and abs(self.y - stair_y) <= 0.05

    def in_safe_zone(self):
        """Retorna True si la persona está en la zona segura."""
        return self.safe_zone_reached

    def get_position(self):
        return self.x, self.y
