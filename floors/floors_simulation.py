from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
import random
import math
import pygame as pg

class Texture:
    def __init__(self, path):
        pg.init()
        self.texture_id = None
        self.load_texture(path)
        
    def load_texture(self, path):
        texture_surface = pg.image.load(path)
        texture_data = pg.image.tostring(texture_surface, "RGBA", 1)
        width, height = texture_surface.get_size()

        self.texture_id = glGenTextures(1)  

        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


class Person:
    def __init__(self, start_x, start_y):
        self.x = start_x + random.uniform(-0.1, 0.1)
        self.y = start_y + random.uniform(-0.1, 0.1)
        self.speed = random.uniform(0.005, 0.015)
        self.safe_zone_reached = False
        self.target_safe_zone = None  

    def move_towards_safe_zone(self, safe_zone_position, move_speed, safe_zone_occupied, others):
        safe_x, safe_y = safe_zone_position


        if safe_zone_occupied:
            return

 
        if abs(self.x - safe_x) > 0.01:  
            self.x += move_speed if self.x < safe_x else -move_speed
        if abs(self.y - safe_y) > 0.01:  
            self.y += move_speed if self.y < safe_y else -move_speed

        self.x += random.uniform(-0.002, 0.002)
        self.y += random.uniform(-0.002, 0.002)

        self.avoid_collision(others)

        if abs(self.x - safe_x) <= 0.01 and abs(self.y - safe_y) <= 0.01:
            self.safe_zone_reached = True
            self.target_safe_zone = None  

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


import random

class FloorsSimulation(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)


        self.floors = [
            [], 
            [Person(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4)) for _ in range(10)], 
            [Person(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4)) for _ in range(10)], 
            [Person(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4)) for _ in range(10)], 
            [Person(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4)) for _ in range(10)]
        ]

        self.stair_positions = [
            (0.6, 0.0), (-0.6, 0.0), (0.6, 0.0), (0.0, -0.6), (0.6, 0.0)
        ]

        self.safe_zone_positions = [
            [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)] for _ in range(5)
        ]

        self.safe_zone_occupied = [[False, False, False, False] for _ in range(5)]

        self.person_safe_zone = [
            [random.randint(0, 3) for _ in floor] for floor in self.floors
        ]

        self.safe_zone_limit = [4] * 5  

        # Variables de cámara
        self.camera_angle_x = 0
        self.camera_angle_y = 20
        self.camera_distance = 5
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.last_time = 0
        glutInit()
    
    def assign_safe_zone(self, person, floor_index):

        assigned = False
        for zone_index in range(4):
            if not self.safe_zone_occupied[floor_index][zone_index]:
                if self.safe_zone_occupied[floor_index].count(True) < self.safe_zone_limit[floor_index]:
                    self.safe_zone_occupied[floor_index][zone_index] = True
                    self.person_safe_zone[floor_index].append(zone_index)
                    assigned = True
                    break

        if not assigned:
            person.move_towards_stair(self.stair_positions[floor_index], 0.08, self.floors[floor_index])



    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)


        self.safe_zone_texture = Texture("assets/safe_zone_sign.png")
        self.stair_texture = Texture("assets/stair_sign.png")
        self.floor_texture = Texture("assets/floor.jpg")



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
        glColor4f(*color)
        glPushMatrix()
        glTranslatef(x, y, z)
        glutSolidCube(size)
        glPopMatrix()

    def draw_textured_prism(self, x, y, z, size, texture):
        height = size * 2.7  
        size /= 1.5 


        tremor_amplitude = 0.005
        tremor_frequency = 4  
        tremor_offset_x = tremor_amplitude * math.sin(glutGet(GLUT_ELAPSED_TIME) * tremor_frequency)
        tremor_offset_z = tremor_amplitude * math.cos(glutGet(GLUT_ELAPSED_TIME) * tremor_frequency)

        glPushMatrix()

        glTranslatef(x + tremor_offset_x, y + height / 2, z + tremor_offset_z)  # Aplicar temblor en X y Z

        glPushAttrib(GL_ALL_ATTRIB_BITS)

        if texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture.texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        else:
            glDisable(GL_TEXTURE_2D)  

        caras = [
            (-size, -height / 2, size, size, -height / 2, size, size, height / 2, size, -size, height / 2, size),
            (-size, -height / 2, -size, -size, height / 2, -size, size, height / 2, -size, size, -height / 2, -size),
            (-size, -height / 2, -size, -size, -height / 2, size, -size, height / 2, size, -size, height / 2, -size),
            (size, -height / 2, -size, size, height / 2, -size, size, height / 2, size, size, -height / 2, size),
            (-size, height / 2, -size, size, height / 2, -size, size, height / 2, size, -size, height / 2, size),
            (-size, -height / 2, -size, -size, -height / 2, size, size, -height / 2, size, size, -height / 2, -size)
        ]

        for i, cara in enumerate(caras):
            glBegin(GL_QUADS)
            if i == 0:  
                if texture:
                    glTexCoord2f(0.0, 0.0)
                glVertex3f(cara[0], cara[1], cara[2])

                if texture:
                    glTexCoord2f(1.0, 0.0)
                glVertex3f(cara[3], cara[4], cara[5])

                if texture:
                    glTexCoord2f(1.0, 1.0)
                glVertex3f(cara[6], cara[7], cara[8])

                if texture:
                    glTexCoord2f(0.0, 1.0)
                glVertex3f(cara[9], cara[10], cara[11])
            else:  
                glColor3f(0.6, 0.6, 0.6)  
                for j in range(0, len(cara), 3):
                    glVertex3f(cara[j], cara[j + 1], cara[j + 2])

            glEnd()

        glPopAttrib()

        glPopMatrix()

    def render_floor_3d(self, floor_index, height):

        glPushAttrib(GL_ALL_ATTRIB_BITS)  

        tremor_amplitude = 0.005
        tremor_frequency = 4
        tremor_offset = tremor_amplitude * math.sin(glutGet(GLUT_ELAPSED_TIME) * tremor_frequency)

        height += tremor_offset 

        glColor3f(1.0, 1.0, 1.0)  
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.floor_texture.texture_id)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.floor_texture.texture_id) 

        floor_size = 0.8
        wall_thickness = 0.025 

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-floor_size, height, -floor_size)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(floor_size, height, -floor_size)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(floor_size, height, floor_size)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-floor_size, height, floor_size)
        glEnd()

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-floor_size, height + wall_thickness, -floor_size)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(floor_size, height + wall_thickness, -floor_size)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(floor_size, height + wall_thickness, floor_size)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-floor_size, height + wall_thickness, floor_size)
        glEnd()

        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-floor_size, height, -floor_size)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-floor_size, height + wall_thickness, -floor_size)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(-floor_size, height + wall_thickness, floor_size)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-floor_size, height, floor_size)

        glTexCoord2f(0.0, 0.0)
        glVertex3f(floor_size, height, -floor_size)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(floor_size, height + wall_thickness, -floor_size)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(floor_size, height + wall_thickness, floor_size)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(floor_size, height, floor_size)

        glTexCoord2f(0.0, 0.0)
        glVertex3f(-floor_size, height, floor_size)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-floor_size, height + wall_thickness, floor_size)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(floor_size, height + wall_thickness, floor_size)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(floor_size, height, floor_size)

        glTexCoord2f(0.0, 0.0)
        glVertex3f(-floor_size, height, -floor_size)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-floor_size, height + wall_thickness, -floor_size)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(floor_size, height + wall_thickness, -floor_size)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(floor_size, height, -floor_size)
        glEnd()

        glDisable(GL_TEXTURE_2D)

        for safe_zone in self.safe_zone_positions[floor_index]:
            safe_x, safe_z = safe_zone
            self.draw_textured_prism(safe_x, height + 0.02, safe_z, 0.1, self.safe_zone_texture)  # Zona segura

        stair_x, stair_z = self.stair_positions[floor_index]
        self.draw_textured_prism(stair_x, height + 0.02, stair_z, 0.1, self.stair_texture)  # Escalera
        glPopAttrib()  

    def render_people_3d(self, floor_index, height, delta_time):
        glPushAttrib(GL_ALL_ATTRIB_BITS)

        glDisable(GL_TEXTURE_2D)
        glColor3f(1.0, 1.0, 1.0)  

        move_speed = 0.08  
        people_on_floor = self.floors[floor_index]
        safe_zone_occupied = self.safe_zone_occupied[floor_index]


        to_remove = []

        num_safe_zone = min(4, len(people_on_floor))
        safe_zone_people = people_on_floor[:num_safe_zone]
        stair_people = people_on_floor[num_safe_zone:]

        safe_zone_radius = 0.8 

        for person_index, person in enumerate(safe_zone_people):
            # Ignorar si ya está en una zona segura
            if person.in_safe_zone():
                continue

            # Obtener la zona segura asignada
            target_zone_index = self.person_safe_zone[floor_index][person_index]
            target_zone_pos = self.safe_zone_positions[floor_index][target_zone_index]

            # Generar una posición aleatoria dentro del radio de la zona segura (alrededor del pilar)
            target_zone_pos_x = target_zone_pos[0] + random.uniform(-safe_zone_radius, safe_zone_radius)
            target_zone_pos_y = target_zone_pos[1] + random.uniform(-safe_zone_radius, safe_zone_radius)

            # Verificar si la zona segura ya está ocupada
            if not safe_zone_occupied[target_zone_index]:
                # Mover hacia la zona segura, asegurándose de que no entre en el pilar
                person.move_towards_safe_zone(
                    (target_zone_pos_x, target_zone_pos_y),
                    move_speed * delta_time,
                    safe_zone_occupied[target_zone_index],
                    people_on_floor
                )

                # Marcar zona como ocupada si llegó
                if person.in_safe_zone():
                    safe_zone_occupied[target_zone_index] = True

                # Persona que va a zona segura (amarillo)
                self.draw_cube(person.x, height + 0.05, person.y, 0.04, (1.0, 1.0, 0.0, 1.0))  # Amarillo
            else:
                # Si la zona está ocupada, dirigir a la persona a la escalera
                person.move_towards_stair(
                    self.stair_positions[floor_index],
                    move_speed * delta_time,
                    people_on_floor
                )

                # Dibujar la persona en movimiento hacia las escaleras (rojo)
                self.draw_cube(person.x, height + 0.05, person.y, 0.04, (1.0, 0.0, 0.0, 1.0))  # Rojo

        # Manejar personas hacia las escaleras (para las que ya no están en zona segura)
        for person in stair_people:
            # Si la persona no está en una zona segura, mover hacia las escaleras
            if not person.in_safe_zone():
                person.move_towards_stair(
                    self.stair_positions[floor_index],
                    move_speed * delta_time,
                    people_on_floor
                )

            # Si llegó a la escalera, mover al siguiente piso
            if person.reached_stair(self.stair_positions[floor_index]) and floor_index > 0:
                self.floors[floor_index - 1].append(person)
                to_remove.append(person)

                # Actualizar sincronización de zonas seguras
                if len(self.person_safe_zone[floor_index]) > 0:
                    self.person_safe_zone[floor_index - 1].append(
                        self.person_safe_zone[floor_index].pop(0)
                    )

            # Dibujar la persona en movimiento hacia las escaleras (rojo)
            self.draw_cube(person.x, height + 0.05, person.y, 0.04, (1.0, 0.0, 0.0, 1.0))  # Rojo

        # Eliminar personas transferidas al siguiente piso
        for person in to_remove:
            self.floors[floor_index].remove(person)
        glPopAttrib()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_mouse_x
        dy = event.y() - self.last_mouse_y
        
        self.camera_angle_x += dx * 0.2  
        self.camera_angle_y -= dy * 0.2
        
        self.camera_angle_y = max(-90.0, min(90.0, self.camera_angle_y))

        self.last_mouse_x = event.x()
        self.last_mouse_y = event.y()
        
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.camera_distance -= delta / 1200.0 
        self.camera_distance = max(1.0, min(10.0, self.camera_distance))  
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_x = event.x()
            self.last_mouse_y = event.y()