import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import random
import pygame as pg  # Asegúrate de tener pygame instalado

class Texture:
    def __init__(self, path):
        pg.init()
        self.texture_id = self.load_texture(path)

    def load_texture(self, path):
        texture_surface = pg.image.load(path)
        texture_data = pg.image.tostring(texture_surface, "RGBA", 1)
        width, height = texture_surface.get_size()

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return texture_id

class VentanaOpenGL(QOpenGLWidget):
    def __init__(self):
        super(VentanaOpenGL, self).__init__()
        self.angle_x = 0
        self.angle_y = 0
        self.last_pos = None
        self.mouse_pressed = False
        self.zoom = -10

        self.setWindowState(Qt.WindowMaximized)
        self.edificios = self.generar_edificios()
        self.texture_loader = None

        # Inicializa el temporizador
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animar_edificios)  # Conectar el temporizador a la función de animación
        self.timer.start(100)  # Llama a la función cada 100 ms (ajusta este valor según tu necesidad)


    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_TEXTURE_2D)

        # Cargar la textura aquí
        self.texture_loader = Texture('assets/spray.jpg')  # Ruta a tu textura

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
    # Establecer el color de fondo (celeste)
        glClearColor(0.5, 0.7, 1.0, 1.0)  # Color celeste (RGB)
        
        # Limpiar el búfer de color y profundidad
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glLoadIdentity()

        # Ajustar la cámara según el valor de zoom
        glTranslatef(0, -2, self.zoom)  # Usar el valor de zoom para la posición de la cámara
        glRotatef(self.angle_x, 1, 0, 0)
        glRotatef(self.angle_y, 0, 1, 0)

        # Dibujar el suelo
        self.dibujar_suelo()

        # Dibujar edificios
        self.dibujar_edificios()

    def dibujar_suelo(self):
        # Configurar el color del suelo (por ejemplo, verde claro)
        glColor3f(0.3, 0.5, 0.3)  # Color verde claro

        # Comenzar a dibujar el suelo como un cuadrado
        glBegin(GL_QUADS)
        
        # Definir los vértices del suelo
        glVertex3f(-10, 0, -10)  # Vértice inferior izquierdo
        glVertex3f(10, 0, -10)   # Vértice inferior derecho
        glVertex3f(10, 0, 10)    # Vértice superior derecho
        glVertex3f(-10, 0, 10)   # Vértice superior izquierdo

        glEnd()

    def generar_edificios(self):
        edificios = []
        for _ in range(10):  # Cambiar la cantidad de filas a 10
            fila = []
            for _ in range(10):  # Cambiar la cantidad de columnas a 10
                width = 0.8
                depth = 0.8
                height = random.uniform(1.5, 3.0)
                fila.append((width, height, depth))
            edificios.append(fila)
        return edificios

    def desplazamiento_temblor(self):
        # Genera un pequeño desplazamiento aleatorio
        offset_x = random.uniform(-0.05, 0.05)
        offset_y = random.uniform(-0.05, 0.05)
        offset_z = random.uniform(-0.05, 0.05)
        return offset_x, offset_y, offset_z

    def dibujar_edificios(self):
        for x in range(10):
            for z in range(10):
                width, height, depth = self.edificios[x][z]
                self.dibujar_prisma(x * 1.2 - 6, height / 2 - 1, z * 1.2 - 6, width, height, depth)

    def dibujar_prisma(self, x, y, z, width, height, depth):
        glPushMatrix()

        # Aplicar desplazamiento de temblor
        offset_x, offset_y, offset_z = self.desplazamiento_temblor()
        
        glTranslatef(x + offset_x, y + offset_y, z + offset_z)  # Ajustar posición con desplazamiento
        glScalef(width, height, depth)  # Escalar en los 3 ejes

        # Parte frontal
        glBindTexture(GL_TEXTURE_2D, self.texture_loader.texture_id)  # Usar la textura cargada
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-0.5, -0.5, 0.5)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(0.5, -0.5, 0.5)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(0.5, 0.5, 0.5)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-0.5, 0.5, 0.5)
        glEnd()

        # Parte trasera
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-0.5, -0.5, -0.5)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(0.5, -0.5, -0.5)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(0.5, 0.5, -0.5)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-0.5, 0.5, -0.5)
        glEnd()

        # Parte lateral derecha
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(0.5, -0.5, -0.5)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(0.5, -0.5, 0.5)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(0.5, 0.5, 0.5)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(0.5, 0.5, -0.5)
        glEnd()

        # Parte lateral izquierda
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-0.5, -0.5, 0.5)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(-0.5, -0.5, -0.5)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(-0.5, 0.5, -0.5)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(-0.5, 0.5, 0.5)
        glEnd()

        # Parte superior (sin textura, color blanco)
        glColor3f(1.0, 1.0, 1.0)  # Cambiar el color a blanco
        glBegin(GL_QUADS)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glEnd()

        # Parte inferior (sin textura, color blanco)
        glBegin(GL_QUADS)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, -0.5)
        glEnd()

        glPopMatrix()

    def wheelEvent(self, event):
        self.zoom += event.angleDelta().y() / 120.0  # Ajustar el zoom según el desplazamiento de la rueda
        self.zoom = max(-20, min(-1, self.zoom))  # Limitar el rango del zoom
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            dx = event.x() - self.last_pos.x()
            dy = event.y() - self.last_pos.y()
            self.angle_y += dx * 0.5
            
            # Limitar el ángulo de inclinación en el eje X (para que no puedas ver debajo del suelo)
            self.angle_x = max(0, min(30, self.angle_x - dy * 0.5))  # Ángulo limitado entre -90 y 0 grados
            
            self.last_pos = event.pos()
            self.update()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False

    def animar_edificios(self):
        # Aquí puedes actualizar la posición de los edificios
        for x in range(len(self.edificios)):
            for z in range(len(self.edificios[x])):
                # Llama a la función que genera el desplazamiento de temblor
                offset_x, offset_y, offset_z = self.desplazamiento_temblor()
                # Aplica el desplazamiento directamente a los edificios
                self.edificios[x][z] = (self.edificios[x][z][0],
                                        self.edificios[x][z][1] + offset_y,  # Aquí puedes aplicar el offset
                                        self.edificios[x][z][2])
        
        self.update()  # Actualiza la ventana para reflejar los cambios


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaOpenGL()
    ventana.show()
    sys.exit(app.exec_())
