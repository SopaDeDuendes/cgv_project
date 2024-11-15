from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
import random
import math
import time

class Person:
    def __init__(self, start_x, start_y):
        self.x = start_x + random.uniform(-0.1, 0.1)
        self.y = start_y + random.uniform(-0.1, 0.1)
        self.speed = random.uniform(0.005, 0.015)
        self.safe_zone_reached = False
        self.time_to_safe_zone = None  # Tiempo para llegar a la zona segura
        self.start_time = None         # Momento de inicio de movimiento

    def start_timer(self, current_time):
        """Inicia el temporizador al comienzo del movimiento."""
        if self.start_time is None:
            self.start_time = current_time

    def record_time_to_safe_zone(self, current_time):
        """Registra el tiempo cuando alcanza la zona segura o sale."""
        if self.time_to_safe_zone is None:
            self.time_to_safe_zone = current_time - self.start_time

    def move_towards_safe_zone(self, safe_zone_position, move_speed, safe_zone_occupied, others):
        safe_x, safe_y = safe_zone_position

        # Si la zona segura ya está ocupada, no permitimos que esta persona entre
        if safe_zone_occupied:
            return

        # Calcular desplazamiento hacia la zona segura
        if abs(self.x - safe_x) > 0.01:
            self.x += move_speed if self.x < safe_x else -move_speed
        if abs(self.y - safe_y) > 0.01:
            self.y += move_speed if self.y < safe_y else -move_speed

        # Aleatoriedad en el movimiento
        self.x += random.uniform(-0.002, 0.002)
        self.y += random.uniform(-0.002, 0.002)

        # Evitar colisiones con otros
        self.avoid_collision(others)

        # Comprobar si ha llegado a la zona segura
        if abs(self.x - safe_x) <= 0.01 and abs(self.y - safe_y) <= 0.01:
            self.safe_zone_reached = True

        if self.safe_zone_reached:
            self.record_time_to_safe_zone(time.perf_counter())

    def move_towards_stair(self, stair_position, move_speed, others):
        stair_x, stair_y = stair_position
        if abs(self.x - stair_x) > 0.01:
            self.x += move_speed if self.x < stair_x else -move_speed
        if abs(self.y - stair_y) > 0.01:
            self.y += move_speed if self.y < stair_y else -move_speed

        # Aleatoriedad en el movimiento
        self.x += random.uniform(-0.002, 0.002)
        self.y += random.uniform(-0.002, 0.002)

        # Evitar colisiones con otros
        self.avoid_collision(others)

    def avoid_collision(self, others):
        # Desvío si está muy cerca de otras personas
        for other in others:
            if other is not self:
                distance_x = self.x - other.x
                distance_y = self.y - other.y
                distance = (distance_x**2 + distance_y**2)**0.5

                # Si la distancia es menor a un umbral, se desvía ligeramente
                if distance < 0.05:
                    self.x += random.uniform(-0.01, 0.01)
                    self.y += random.uniform(-0.01, 0.01)

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


class FloorsSimulation(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

        # Posiciones de personas, escaleras y zonas seguras
        self.floors = [
            [], [], 
            [Person(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)) for _ in range(10)], 
            [Person(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)) for _ in range(10)], 
            [Person(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)) for _ in range(10)]
        ]

        # Cambiamos las posiciones de escaleras y zonas seguras a (x, z)
        self.stair_positions = [
            (0.0, 0.6), (-0.6, 0.0), (0.6, 0.0), (0.0, -0.6), (0.6, 0.0)
        ]

        self.safe_zone_positions = [
            (-0.6, -0.6), (0.6, -0.6), (-0.6, 0.6), (0.6, 0.6), (-0.6, 0.6)
        ]


        self.safe_zone_occupied = [False] * 5

        # Variables de cámara
        self.camera_angle_x = 0
        self.camera_angle_y = 20  # Ajustar este valor para cambiar la vista vertical
        self.camera_distance = 5   # Aumentar la distancia para ver todo el edificio
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.last_time = 0  # Tiempo de la última actualización
        glutInit()
        
    def get_times_to_safety(self):
        """Devuelve los tiempos de las personas para llegar a la seguridad."""
        results = []
        for floor in self.floors:
            for person in floor:
                if person.time_to_safe_zone is not None:
                    results.append(person.time_to_safe_zone)
        return results
    
    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w / h if h > 0 else 1, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.set_camera()

        current_time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        delta_time = current_time - self.last_time
        self.last_time = current_time

        for i, _ in enumerate(self.floors):
            height = i * 0.3
            self.render_floor_3d(i, height)
            self.render_people_3d(i, height, delta_time)

        glFlush()

    def set_camera(self):
        glLoadIdentity()
        camera_x = self.camera_distance * math.sin(math.radians(self.camera_angle_x)) * math.cos(math.radians(self.camera_angle_y))
        camera_z = self.camera_distance * math.sin(math.radians(self.camera_angle_y))
        camera_y = self.camera_distance * math.cos(math.radians(self.camera_angle_x)) * math.cos(math.radians(self.camera_angle_y))
        gluLookAt(camera_x, camera_y, camera_z, 0, 0, 0, 0, 1, 0)

    def draw_cube(self, x, y, z, size, color):
        glColor3f(*color)
        glPushMatrix()
        glTranslatef(x, y, z)
        glutSolidCube(size)
        glPopMatrix()

    def render_floor_3d(self, floor_index, height):
        glColor3f(0.8, 0.8, 0.8)
        glBegin(GL_QUADS)
        glVertex3f(-0.7, height, -0.7)
        glVertex3f(0.7, height, -0.7)
        glVertex3f(0.7, height, 0.7)
        glVertex3f(-0.7, height, 0.7)
        glEnd()
        
        # Renderiza las paredes
        glColor3f(0.5, 0.5, 0.5)
        wall_height = 0.1
        self.draw_cube(-0.5, height + wall_height / 2, 0, 0.02, (0.5, 0.5, 0.5))
        self.draw_cube(0.5, height + wall_height / 2, 0, 0.02, (0.5, 0.5, 0.5))
        self.draw_cube(0, height + wall_height / 2, 0.5, 0.02, (0.5, 0.5, 0.5))
        self.draw_cube(0, height + wall_height / 2, -0.5, 0.02, (0.5, 0.5, 0.5))
        
        # Zonas seguras y escaleras
        safe_x, safe_z = self.safe_zone_positions[floor_index]
        self.draw_cube(safe_x, height + 0.02, safe_z, 0.1, (0.0, 1.0, 0.0))
        stair_x, stair_z = self.stair_positions[floor_index]
        self.draw_cube(stair_x, height + 0.02, stair_z, 0.1, (0.3, 0.3, 0.3))


    def render_people_3d(self, floor_index, height, delta_time):
        move_speed = 0.05  # Velocidad de movimiento
        people_on_floor = self.floors[floor_index]

        # Verificar si alguien ya está en la zona segura
        safe_zone_occupied = any(person.in_safe_zone() for person in people_on_floor)

        for person in people_on_floor:
            # Inicia el temporizador si aún no lo ha hecho
            person.start_timer(time.perf_counter())

            if person.in_safe_zone():
                continue  # Si la persona ya está en la zona segura, no hacer nada

            # Mueve la persona hacia la zona segura solo si no está ocupada
            person.move_towards_safe_zone(
                self.safe_zone_positions[floor_index],
                move_speed * delta_time,
                safe_zone_occupied,
                people_on_floor
            )

            if person.in_safe_zone():
                safe_zone_occupied = True  # Marca la zona segura como ocupada
                person.record_time_to_safe_zone(time.perf_counter())  # Registra el tiempo

            # Si la zona segura está ocupada, mueve la persona hacia las escaleras
            if safe_zone_occupied:
                person.move_towards_stair(
                    self.stair_positions[floor_index],
                    move_speed * delta_time,
                    people_on_floor
                )
                if person.reached_stair(self.stair_positions[floor_index]) and floor_index > 0:
                    self.floors[floor_index - 1].append(person)  # Mueve la persona al otro piso
                    self.floors[floor_index].remove(person)
                    person.record_time_to_safe_zone(time.perf_counter())  # Registra el tiempo al salir

            # Dibuja la persona en el piso
            self.draw_cube(person.x, height + 0.05, person.y, 0.04, (1.0, 0.0, 0.0))


    def mouseMoveEvent(self, event):
        # Cálculo del desplazamiento del mouse
        dx = event.x() - self.last_mouse_x
        dy = event.y() - self.last_mouse_y
        
        # Ajuste de ángulos de la cámara
        self.camera_angle_x += dx * 0.2
        self.camera_angle_y -= dy * 0.2
        
        
        # Actualizar las coordenadas del mouse
        self.last_mouse_x = event.x()
        self.last_mouse_y = event.y()
        
        # Solicitar actualización de la escena
        self.update()

    def wheelEvent(self, event):
        # Movimiento de la rueda para ajustar la distancia de la cámara
        delta = event.angleDelta().y()
        self.camera_distance -= delta / 1200.0  # Ajusta la sensibilidad aquí
        self.camera_distance = max(1.0, min(10.0, self.camera_distance))  # Limita el rango
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Guardar la posición inicial del mouse cuando se hace clic izquierdo
            self.last_mouse_x = event.x()
            self.last_mouse_y = event.y()


