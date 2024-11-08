import random


class Person:
    def __init__(self, start_x, start_y):
        self.x = start_x + random.uniform(-0.1, 0.1)
        self.y = start_y + random.uniform(-0.1, 0.1)
        self.speed = random.uniform(0.005, 0.015)
        self.safe_zone_reached = False

    def move_towards_safe_zone(self, safe_zone_position, move_speed, safe_zone_occupied):
        safe_x, safe_y = safe_zone_position

        # Si la zona segura ya está ocupada, no permitimos que esta persona entre
        if safe_zone_occupied:
            return

        if abs(self.x - safe_x) > 0.01:
            self.x += move_speed if self.x < safe_x else -move_speed
        if abs(self.y - safe_y) > 0.01:
            self.y += move_speed if self.y < safe_y else -move_speed

        if abs(self.x - safe_x) <= 0.01 and abs(self.y - safe_y) <= 0.01:
            self.safe_zone_reached = True

    def move_towards_stair(self, stair_position, move_speed):
        stair_x, stair_y = stair_position
        if abs(self.x - stair_x) > 0.01:
            self.x += move_speed if self.x < stair_x else -move_speed
        if abs(self.y - stair_y) > 0.01:
            self.y += move_speed if self.y < stair_y else -move_speed

    def reached_stair(self, stair_position):
        # Verifica si la persona ha llegado a la escalera
        stair_x, stair_y = stair_position
        return abs(self.x - stair_x) <= 0.05 and abs(self.y - stair_y) <= 0.05

    def in_safe_zone(self):
        # Retorna True si la persona está en la zona segura
        return self.safe_zone_reached

    def get_position(self):
        # Retorna la posición actual de la persona
        return self.x, self.y
