import sys
from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import pygame as pg  

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

class EarthquakeSimulator(QOpenGLWidget):
    def __init__(self):
        super(EarthquakeSimulator, self).__init__()
        self.angle_x = 0
        self.angle_y = 0
        self.last_pos = None
        self.mouse_pressed = False
        self.zoom = -10

        self.setWindowState(Qt.WindowMaximized)
        self.edificios = self.generar_edificios()
        self.texture_loader = None
    
        # Temporizador para bucle
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animar_edificios)  # Conectar el temporizador a la función de animación
        self.timer.start(100) 


    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_TEXTURE_2D)

        # Cargar la textura 
        self.texture_loader = Texture('assets/spray.jpg')

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        # Color de fondo (celeste)
        glClearColor(0.5, 0.7, 1.0, 1.0)  
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glLoadIdentity()

        # Ajustes de la cámara 
        glTranslatef(0, -2, self.zoom)  # zoom 
        glRotatef(self.angle_x, 1, 0, 0)
        glRotatef(self.angle_y, 0, 1, 0)

        # Suelo
        self.dibujar_suelo()

        # Edificios
        self.dibujar_edificios()

    def dibujar_suelo(self):
        # Color del suelo
        glColor3f(0.3, 0.5, 0.3)  

        glBegin(GL_QUADS)
        
        glVertex3f(-10, 0, -10) 
        glVertex3f(10, 0, -10) 
        glVertex3f(10, 0, 10)   
        glVertex3f(-10, 0, 10) 

        glEnd()

    def generar_edificios(self):
        edificios = []
        for _ in range(10):  # Filas de 10
            fila = []
            for _ in range(10):  # Columnas de 10
                width = 0.8
                depth = 0.8
                height = random.uniform(1.5, 3.0)
                fila.append((width, height, depth))
            edificios.append(fila)
        return edificios

    def desplazamiento_temblor(self):
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
        glBindTexture(GL_TEXTURE_2D, self.texture_loader.texture_id)  # Usar textura
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

        # Parte superior 
        glColor3f(1.0, 1.0, 1.0)  
        glBegin(GL_QUADS)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glEnd()

        # Parte inferior 
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
            
            self.angle_x = max(0, min(30, self.angle_x - dy * 0.5)) 
            
            self.last_pos = event.pos()
            self.update()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False

    def animar_edificios(self):

        for x in range(len(self.edificios)):
            for z in range(len(self.edificios[x])):

                offset_x, offset_y, offset_z = self.desplazamiento_temblor()

                self.edificios[x][z] = (self.edificios[x][z][0],
                                        self.edificios[x][z][1] + offset_y,  
                                        self.edificios[x][z][2])
        
        self.update() 

if __name__ == '__main__':
    import pygame as pg
    pg.init()  # Inicializar Pygame antes de la creación de la ventana

    app = QApplication(sys.argv)    
    ventana = EarthquakeSimulator()
    ventana.show()
    sys.exit(app.exec_())
