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
        """Cambia el piso actual y renderiza el nuevo piso."""
        self.current_floor = floor_index
        self.update() 

    def initializeGL(self):
        """Inicialización de OpenGL (se ejecuta una vez)."""
        self.setFixedSize(1280 , 720) 

    def paintGL(self):
        """Función para renderizar usando OpenGL."""
        render_floor_with_people(self.current_floor)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Simulador de Terremotos')
        self.current_floor = 4  # Comienza en el piso 5 
        self.total_floors = 5

        self.opengl_widget = OpenGLWidget(self)

        # Label que muestra en qué piso estamos
        self.floor_label = QLabel(f"Piso Actual: {self.current_floor + 1}", self)
        self.floor_label.setAlignment(Qt.AlignCenter)

        # Botones para desplazarse entre pisos
        self.prev_button = QPushButton('⬅ Piso Anterior')
        self.next_button = QPushButton('Piso Siguiente ➡')

        self.prev_button.clicked.connect(self.prev_floor)
        self.next_button.clicked.connect(self.next_floor)

        # Layout horizontal para los botones a los costados
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.floor_label)
        button_layout.addWidget(self.next_button)

        # Layout principal vertical que incluye OpenGL y los botones
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.opengl_widget)
        main_layout.addLayout(button_layout)

        # Widget principal
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Timer para actualizar la simulación
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(100)  # Bucle de 100 ms

    def prev_floor(self):
        """Función para ir al piso anterior."""
        if self.current_floor > 0:
            self.current_floor -= 1
            self.update_display()

    def next_floor(self):
        """Función para ir al piso siguiente."""
        if self.current_floor < self.total_floors - 1:
            self.current_floor += 1
            self.update_display()

    def update_display(self):
        """Actualiza el label y el widget OpenGL para reflejar el piso actual."""
        self.floor_label.setText(f"Piso Actual: {self.current_floor + 1}")
        self.opengl_widget.set_floor(self.current_floor)  # Actualiza el piso en OpenGL

    def update_simulation(self):
        """Función que fuerza el redibujado de OpenGL cada vez que se actualiza."""
        self.opengl_widget.update()

def start_simulation():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
