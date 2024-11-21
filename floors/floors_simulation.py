from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QFont
import random
import math
import pygame
from utils.texture import Texture
from floors.person import Person

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


        pygame.init()
        pygame.mixer.init()  # Asegúrate de inicializar el mezclador de sonidos de pygame
        self.sound_safe = pygame.mixer.Sound("assets/safe_sound.wav")  # Aquí cargas el archivo de sonido adecuado
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
        glColor3f(1.0, 1.0, 1.0)  # Color por defecto

        move_speed = 0.08
        people_on_floor = self.floors[floor_index]
        safe_zone_occupied = self.safe_zone_occupied[floor_index]

        to_remove = []

        num_safe_zone = min(4, len(people_on_floor))
        safe_zone_people = people_on_floor[:num_safe_zone]
        stair_people = people_on_floor[num_safe_zone:]

        safe_zone_radius = 0.8
        stair_radius = 0.2

        # Manejo de personas en la zona segura
        for person_index, person in enumerate(safe_zone_people):
            if person.in_safe_zone():
                # Si ya está en la zona segura, marcarla como completamente a salvo
                if not person.is_safe():
                    person.is_completely_safe = True  # Cambia el estado de seguridad

                    # Reproducir sonido si la persona está completamente a salvo
                    self.sound_safe.play()

            target_zone_index = self.person_safe_zone[floor_index][person_index]
            target_zone_pos = self.safe_zone_positions[floor_index][target_zone_index]

            target_zone_pos_x = target_zone_pos[0] + random.uniform(-safe_zone_radius, safe_zone_radius)
            target_zone_pos_y = target_zone_pos[1] + random.uniform(-safe_zone_radius, safe_zone_radius)

            distance_to_zone = math.sqrt((person.x - target_zone_pos[0]) ** 2 + (person.y - target_zone_pos[1]) ** 2)

            if not safe_zone_occupied[target_zone_index]:
                person.move_towards_safe_zone(
                    (target_zone_pos_x, target_zone_pos_y),
                    move_speed * delta_time,
                    safe_zone_occupied[target_zone_index],
                    people_on_floor
                )

                if person.in_safe_zone():
                    # Reproducir sonido si la persona está completamente a salvo
                    self.sound_safe.play()
                    safe_zone_occupied[target_zone_index] = True

                # Si la persona está completamente a salvo, podemos usar otro color para diferenciarla
                color = (0.0, 1.0, 0.0, 1.0) if person.is_safe() else (1.0, 0.0, 0.0, 1.0)
                self.draw_cube(person.x, height + 0.05, person.y, 0.04, color)

            else:
                person.move_towards_stair(
                    self.stair_positions[floor_index],
                    move_speed * delta_time,
                    people_on_floor
                )
                self.draw_cube(person.x, height + 0.05, person.y, 0.04, (1.0, 0.0, 0.0, 1.0))

        # Manejo de personas que se dirigen hacia las escaleras
        for person in stair_people:
            distance_to_stair = math.sqrt(
                (person.x - self.stair_positions[floor_index][0]) ** 2 +
                (person.y - self.stair_positions[floor_index][1]) ** 2
            )

            if not person.in_safe_zone():
                person.move_towards_stair(
                    self.stair_positions[floor_index],
                    move_speed * delta_time,
                    people_on_floor
                )

            if person.reached_stair(self.stair_positions[floor_index]) and floor_index > 0:
                self.floors[floor_index - 1].append(person)
                to_remove.append(person)

                if len(self.person_safe_zone[floor_index]) > 0:
                    self.person_safe_zone[floor_index - 1].append(
                        self.person_safe_zone[floor_index].pop(0)
                    )

            color = (0.0, 1.0, 0.0, 1.0) if distance_to_stair <= stair_radius else (1.0, 0.0, 0.0, 1.0)
            self.draw_cube(person.x, height + 0.05, person.y, 0.04, color)

        
        # Solo eliminar a las personas que realmente llegaron a las escaleras
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