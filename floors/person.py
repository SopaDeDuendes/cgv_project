import random 
import math

class Person:
    def __init__(self, start_x, start_y):
        self.x = start_x + random.uniform(-0.1, 0.1)
        self.y = start_y + random.uniform(-0.1, 0.1)
        self.speed = random.uniform(0.005, 0.015)
        self.safe_zone_reached = False
        self.target_safe_zone = None  
        self.is_completely_safe = False  # Atributo que indica si está completamente a salvo

    def move_towards_safe_zone(self, safe_zone_position, move_speed, safe_zone_occupied, others, target_radius=0.09):
        safe_x, safe_y = safe_zone_position

        # Si la zona está ocupada, no mover la persona
        if safe_zone_occupied:
            return

        # Calcula la distancia actual a la zona segura
        distance_to_safe_zone = math.sqrt((self.x - safe_x) ** 2 + (self.y - safe_y) ** 2)

        # Mueve la persona hacia la zona segura mientras esté fuera del radio objetivo
        if distance_to_safe_zone > target_radius:  # Si está fuera del radio de la zona
            if abs(self.x - safe_x) > 0.01:  
                self.x += move_speed if self.x < safe_x else -move_speed
            if abs(self.y - safe_y) > 0.01:  
                self.y += move_speed if self.y < safe_y else -move_speed

        # Agregar un pequeño desplazamiento aleatorio
        self.x += random.uniform(-0.002, 0.002)
        self.y += random.uniform(-0.002, 0.002)

        # Evitar colisiones con otras personas
        self.avoid_collision(others)

        # Si la persona ha llegado al radio de la zona segura, simplemente se mantiene cerca
        if distance_to_safe_zone <= target_radius:
            self.x = safe_x  # Mantener la persona dentro de la zona
            self.y = safe_y  # Ajuste de la posición para mantenerla en el radio
            self.target_safe_zone = None  # Descartar la zona de destino

            # Marca a la persona como completamente a salvo
            self.is_completely_safe = True  # Persona completamente a salvo al llegar a la zona segura

    def move_towards_stair(self, stair_position, move_speed, others):
        stair_x, stair_y = stair_position
        if abs(self.x - stair_x) > 0.01:
            self.x += move_speed if self.x < stair_x else -move_speed
        if abs(self.y - stair_y) > 0.01:
            self.y += move_speed if self.y < stair_y else -move_speed

        self.x += random.uniform(-0.002, 0.002)
        self.y += random.uniform(-0.002, 0.002)

        self.avoid_collision(others)

    def avoid_collision(self, others):
        for other in others:
            if other is not self:
                distance_x = self.x - other.x
                distance_y = self.y - other.y
                distance = (distance_x**2 + distance_y**2)**0.5

                if distance < 0.05:
                    self.x += random.uniform(-0.01, 0.01)
                    self.y += random.uniform(-0.01, 0.01)

    def reached_stair(self, stair_position):
        stair_x, stair_y = stair_position
        return abs(self.x - stair_x) <= 0.05 and abs(self.y - stair_y) <= 0.05

    def in_safe_zone(self):
        return self.safe_zone_reached

    def get_position(self):
        return self.x, self.y

    def update(self, safe_zones, stair_position, move_speed, safe_zone_occupied, others, safe_zone_count, safe_zone_limit):
        if safe_zone_count < safe_zone_limit:
            if not self.target_safe_zone:
                self.target_safe_zone = random.choice(safe_zones)

            self.move_towards_safe_zone(self.target_safe_zone, move_speed, safe_zone_occupied, others)
        else:
            self.move_towards_stair(stair_position, move_speed, others)

    def is_safe(self):
        """Devuelve True si la persona está completamente a salvo."""
        return self.is_completely_safe
