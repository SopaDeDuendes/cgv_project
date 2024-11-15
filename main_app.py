# Importamos las clases desde los archivos correspondientes
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication  # Importación de QApplication al principio

# Importaciones locales
from buildings.earthquake import EarthquakeSimulator  # Asegúrate de que el archivo esté en la ruta correcta
from floors.floors_simulation import FloorsSimulation  # Asegúrate de que el archivo esté en la ruta correcta

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Sismo")
        self.setGeometry(100, 100, 1200, 800)

        # Layout principal (disposición horizontal)
        main_layout = QHBoxLayout()

        # Crear aside izquierdo con el título y el botón
        self.left_sidebar = self.create_left_sidebar()
        main_layout.addWidget(self.left_sidebar)

        # Crear el contenedor central con QStackedWidget
        self.central_widget = QStackedWidget()

        # Instancias de las vistas importadas
        self.earthquake_view = EarthquakeSimulator()  # Instancia de la clase EarthquakeSimulator desde building.earthquake
        self.simulator_view = FloorsSimulation()  # Instancia de la clase Simulator desde floors.simulator

        # Agregar las vistas al QStackedWidget
        self.central_widget.addWidget(self.earthquake_view)
        self.central_widget.addWidget(self.simulator_view)
        
        # Mostrar la vista de `simulator_view` por defecto
        self.central_widget.setCurrentWidget(self.earthquake_view)
        
        # Añadir el contenedor principal al layout
        main_layout.addWidget(self.central_widget)

        # Crear el contenedor principal que alojará el layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_left_sidebar(self):
        left_sidebar = QWidget()
        sidebar_layout = QVBoxLayout()

        # Título del aside (sidebar)
        title_label = QLabel("Simulador de Sismo")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")
        sidebar_layout.addWidget(title_label)

        # Botón para iniciar la simulación
        start_button = QPushButton("Iniciar Simulación")
        start_button.clicked.connect(self.switch_to_simulator)
        sidebar_layout.addWidget(start_button)

        # Botón para regresar a la vista de terremoto
        back_button = QPushButton("Volver a la vista de Terremoto")
        back_button.clicked.connect(self.switch_to_earthquake)
        sidebar_layout.addWidget(back_button)

        # Configuración del aside (mínimo tamaño y estilo)
        left_sidebar.setLayout(sidebar_layout)
        left_sidebar.setMinimumWidth(200)
        left_sidebar.setStyleSheet("background-color: lightgray;")

        return left_sidebar

    def switch_to_simulator(self):
        # Cambiar la vista central al simulador
        self.central_widget.setCurrentWidget(self.simulator_view)
        
    def switch_to_earthquake(self):
        # Cambiar la vista central a la vista de terremoto
        self.central_widget.setCurrentWidget(self.earthquake_view)

# Ejecutar la aplicación
app = QApplication([])  # Crear la aplicación al principio

# Crear la ventana principal
main_app = MainApp()
main_app.show()

# Ejecutar el loop de la aplicación
app.exec()
