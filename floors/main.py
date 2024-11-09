import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtOpenGL import QGLWidget
from opengl_renderer import render_floor_with_people
from PyQt5.QtCore import Qt

class OpenGLWidget(QGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.current_floor = 4  # Iniciar en el piso 5 

    def set_floor(self, floor_index):
        self.current_floor = floor_index
        self.update() 

    def initializeGL(self):
        self.setFixedSize(1280 , 720) 

    def paintGL(self):
        render_floor_with_people(self.current_floor)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simulador de Terremotos')
        self.current_floor = 4  # Comienza en el piso 5 
        self.total_floors = 5

        self.opengl_widget = OpenGLWidget(self)
    
        # Layout principal vertical que incluye OpenGL y los botones
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.opengl_widget)

        # Widget principal
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Timer para actualizar la simulación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(100)  # Bucle de 100 ms

    def update_display(self):
        self.floor_label.setText(f"Piso Actual: {self.current_floor + 1}")
        self.opengl_widget.set_floor(self.current_floor)  

    def update_simulation(self):
        self.opengl_widget.update()
# Se inicia la simulacion
def start_simulation():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
