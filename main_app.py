from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication 
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from utils.custom_button import CustomButton
from buildings.earthquake import EarthquakeSimulator  
from floors.floors_simulation import FloorsSimulation  
import pygame

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Sismo")
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QHBoxLayout()

        self.left_sidebar = self.create_left_sidebar()
        main_layout.addWidget(self.left_sidebar)

        self.central_widget = QStackedWidget()
        self.earthquake_view = EarthquakeSimulator()
        self.simulator_view = FloorsSimulation()

        self.central_widget.addWidget(self.earthquake_view)
        self.central_widget.addWidget(self.simulator_view)

        self.central_widget.setCurrentWidget(self.simulator_view)  # Cambiar por la vista inicial

        main_layout.addWidget(self.central_widget)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        # Maximizar la ventana al inicio
        self.showMaximized()

    def update_data(self, data):
        """Actualizar la interfaz con los datos de la simulación"""
        print("Datos recibidos:", data)
        # Aquí puedes mostrar los datos en un QLabel, QListView, etc.

    def create_left_sidebar(self):
        left_sidebar = QWidget()
        sidebar_layout = QVBoxLayout()

        title_label = QLabel("Simulador de Sismo")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: black;")
        sidebar_layout.addWidget(title_label)

        recommendations_label = QLabel("Recomendaciones en caso de Sismo:")
        recommendations_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        sidebar_layout.addWidget(recommendations_label)

        recommendations_text = """
        Recomendaciones proporcionadas por la Plataforma del Estado Peruano.
        
        ANTES DEL SISMO: 

        1. Ubica las zonas seguras y estructuras firmes para protegerte.
        2. Ten preparada una mochila de emergencia.
        3. Participa en los simulacros de sismo de tu barrio.
        4. Educa a los niños de tu casa sobre medidas de precaución.
        5. Contrata un ingeniero para reforzar tu vivienda.

        DURANTE EL SISMO: 

        1. Aléjate de las ventanas y objetos que pueden caerse.
        2. Si no llegas rápido a la salida, busca un espacio seguro.
        3. No llames por teléfono. La línea estará sobrecargada, 
        así que mejor envía mensajes de texto.
        4. No uses ascensor.

        DESPUES DEL SISMO: 

        1. Revisa si hay fugas de gas que podrían causar fuego.
        2. Llamar a los números de emergencia como: los bomberos 116, 
        Cruz Roja (01) 2660481 y el Sistema de Atención Móvil de Urgencia (SAMU) 106.
        3. Auxilia a los heridos.
        4. Ten cuidado con las posibles réplicas. Evita estar cerca a 
        casas que han sido afectadas por el sismo.
        5. Si estás cerca al mar, aléjate de la zona hasta que se 
        descarte la posibilidad de un maremoto.
        """
        recommendations_details = QLabel(recommendations_text)
        recommendations_details.setStyleSheet("font-size: 16px; color: black;")
        sidebar_layout.addWidget(recommendations_details)

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout()

        left_buttons_widget = QWidget()
        left_buttons_layout = QVBoxLayout()
        start_button = CustomButton("Ver Edificio")
        start_button.clicked.connect(self.switch_to_simulator)
        left_buttons_layout.addWidget(start_button)

        back_button = CustomButton("Ver Ciudad")
        back_button.clicked.connect(self.switch_to_earthquake)
        left_buttons_layout.addWidget(back_button)

        left_buttons_widget.setLayout(left_buttons_layout)

        right_buttons_widget = QWidget()
        right_buttons_layout = QVBoxLayout()
        sound_button = QPushButton()
        sound_button.setIcon(QIcon("assets/sound_icon.png"))  
        sound_button.setIconSize(QSize(50, 50))  
        sound_button.clicked.connect(self.toggle_sound) 
        right_buttons_layout.addWidget(sound_button)

        right_buttons_widget.setLayout(right_buttons_layout)

        buttons_layout.addWidget(left_buttons_widget)
        buttons_layout.addWidget(right_buttons_widget)

        buttons_widget.setLayout(buttons_layout)

        sidebar_layout.addWidget(buttons_widget)
        left_sidebar.setLayout(sidebar_layout)
        left_sidebar.setMinimumWidth(250)
        left_sidebar.setStyleSheet("background-color: lightgray;")

        self.media_player = QMediaPlayer()
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile("assets/sirena.wav")))
        self.is_sound_playing = False

        return left_sidebar

    def toggle_sound(self):
        """Reproduce o detiene el sonido usando Pygame con el volumen ajustado."""
        if not hasattr(self, 'pygame_initialized'):
            pygame.mixer.init()
            self.pygame_initialized = True

        if self.is_sound_playing:
            pygame.mixer.music.stop()
            print("Sonido apagado")
        else:
            pygame.mixer.music.load("assets/sirena.wav")    
            pygame.mixer.music.set_volume(0.5)  
            pygame.mixer.music.play(-1)  
            print("Sonido encendido")
        self.is_sound_playing = not self.is_sound_playing
    def switch_to_simulator(self):
        self.central_widget.setCurrentWidget(self.simulator_view)
        
    def switch_to_earthquake(self):
        self.central_widget.setCurrentWidget(self.earthquake_view)

app = QApplication([]) 

main_app = MainApp()
main_app.show()

app.exec()