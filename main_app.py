from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication 
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl,QTimer
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
        self.earthquake_view = EarthquakeSimulator()  # Vista de terremoto
        self.simulator_view = FloorsSimulation()  # Vista de simulador de pisos

        self.central_widget.addWidget(self.earthquake_view)
        self.central_widget.addWidget(self.simulator_view)

        # Cambiar la vista inicial al simulador
        self.central_widget.setCurrentWidget(self.simulator_view)

        # Mostrar temporizador y descripción desde el inicio
        self.timer_label.show()
        self.timer_description.show()

        main_layout.addWidget(self.central_widget)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        # Maximizar la ventana al inicio
        self.showMaximized()

        # Inicializar temporizador
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_time = 0
        self.is_simulation_running = False
        self.is_timer_stopped = False

        self.switch_to_simulator()

        self.initialize_sound()

        self.simulator_view.signal_all_safe.connect(self.on_all_safe)
            
    def update_timer(self):
        if self.is_simulation_running:
            self.elapsed_time += 1
            minutes = self.elapsed_time // 60
            seconds = self.elapsed_time % 60
            self.timer_label.setText(f"Tiempo: {minutes}:{seconds:02d}")

            if self.elapsed_time == 51:
                self.stop_timer()
                self.play_congratulations_sound()
                self.show_congratulations_window()

    def show_congratulations_window(self):
        self.congratulations_window = QMainWindow(self)
        self.congratulations_window.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.congratulations_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        central_widget = QWidget(self.congratulations_window)
        layout = QVBoxLayout(central_widget)

        congratulations_label = QLabel("¡FELICITACIONES!\nTODOS ESTÁN A SALVO")
        congratulations_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        congratulations_label.setStyleSheet("""
            font-size: 64px;
            font-weight: bold;
            color: white;
            background-color: rgba(0, 128, 0, 0.8); 
            padding: 20px;
            border-radius: 20px;
        """)
        layout.addWidget(congratulations_label)

        self.congratulations_window.setCentralWidget(central_widget)
        self.congratulations_window.resize(800, 400)
        screen = QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.congratulations_window.width()) // 2
        y = (screen.height() - self.congratulations_window.height()) // 2
        self.congratulations_window.move(x, y)

        self.congratulations_window.show()

    def on_all_safe(self, all_safe):
        if all_safe:
            self.stop_timer()
            self.play_congratulations_sound()

    def play_congratulations_sound(self):
        if not hasattr(self, 'pygame_initialized'):
            pygame.mixer.init()
            self.pygame_initialized = True

        pygame.mixer.music.stop()  
        pygame.mixer.Sound("assets/congratulations.wav").play()  
        print("Efecto de sonido de felicitaciones reproducido.")

    def switch_to_simulator(self):
        """Cambiar a la vista de simulación de edificios."""
        self.central_widget.setCurrentWidget(self.simulator_view)
        self.timer_label.show()  
        self.timer_description.show() 


        if not self.is_simulation_running and not self.is_timer_stopped:
            self.start_timer()

        self.hide_recommendations()  

    def switch_to_earthquake(self):
        """Cambiar a la vista de simulación de terremoto."""
        self.central_widget.setCurrentWidget(self.earthquake_view)
        self.timer_label.hide() 
        self.timer_description.hide()  
        self.show_recommendations()

        if hasattr(self, 'congratulations_window') and self.congratulations_window is not None:
            self.congratulations_window.close()
            self.congratulations_window = None  

    def start_timer(self):
        if not self.is_simulation_running:
            self.is_simulation_running = True
            self.is_timer_stopped = False  
            self.timer.start(1000)  

    def stop_timer(self):
        """Detiene el temporizador."""
        self.is_simulation_running = False
        self.is_timer_stopped = True  
        self.timer.stop()

    def create_left_sidebar(self):
        left_sidebar = QWidget()
        sidebar_layout = QVBoxLayout()

        title_label = QLabel("Simulador de Sismo <br> (Vista de Edificio con Rayos-X)")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: black;")
        sidebar_layout.addWidget(title_label)
        self.recommendations_text = """
        Recomendaciones proporcionadas por la Plataforma del Estado Peruano.
        
        <b>ANTES DEL SISMO:</b>

        1. Ubica las zonas seguras y estructuras firmes para protegerte.
        2. Ten preparada una mochila de emergencia.
        3. Participa en los simulacros de sismo de tu barrio.
        4. Educa a los niños de tu casa sobre medidas de precaución.
        5. Contrata un ingeniero para reforzar tu vivienda.

        <b>DURANTE EL SISMO:</b>

        1. Aléjate de las ventanas y objetos que pueden caerse.
        2. Si no llegas rápido a la salida, busca un espacio seguro.
        3. No llames por teléfono. La línea estará sobrecargada, 
        así que mejor envía mensajes de texto.
        4. No uses ascensor.

        <b>DESPUES DEL SISMO:</b>

        1. Revisa si hay fugas de gas que podrían causar fuego.
        2. Llamar a los números de emergencia como: los bomberos 116, 
        Cruz Roja (01) 2660481 y el Sistema de Atención Móvil de Urgencia (SAMU) 106.
        3. Auxilia a los heridos.
        4. Ten cuidado con las posibles réplicas. Evita estar cerca a 
        casas que han sido afectadas por el sismo.
        5. Si estás cerca al mar, aléjate de la zona hasta que se 
        descarte la posibilidad de un maremoto.
        """
        self.recommendations_details = QLabel(self.recommendations_text)
        self.recommendations_details.setStyleSheet("font-size: 16px; color: black;")
        sidebar_layout.addWidget(self.recommendations_details)

        self.timer_label = QLabel("Tiempo: 0:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 42px; font-weight: bold; color: black;")
        sidebar_layout.addWidget(self.timer_label)


        self.simulation_description = """
        <b>LOS CUBOS REPRESENTAN PERSONAS EVACUANDO</b> <br><br><br>
        
        🟥 = Personas que toman una decisión que los pone en peligro<br><br>
        🟩 =  Personas que toman la decisión de ponerse<br>
        a salvo, al lado de columnas o buscando las escaleras<br><br>
        
        <img src="assets/stair_sign.png" width="40" height="40">  = Señal de Salida a utilizar en caso de emergencias <br>
        <img src="assets/safe_zone_sign.png" width="40" height="40"> = Señal que indica una Zona segura en caso de sismos <br>
        <img src="assets/exit_sign.png" width="40" height="40"> = Señal que marca la salida <br>

        """

        self.timer_description = QLabel(self.simulation_description)
        self.timer_description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_description.setStyleSheet("font-size: 14px; color: black; margin-top: 10px;")
        self.timer_description.setVisible(False)  
        sidebar_layout.addWidget(self.timer_description)


        self.recommendations_details.hide()

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
        self.sound_button = QPushButton()
        self.sound_button.setIcon(QIcon("assets/sound_on_icon.png"))  
        self.sound_button.setIconSize(QSize(50, 50))
        self.sound_button.clicked.connect(self.toggle_sound)
        self.sound_button.setStyleSheet("border: none; background: transparent;")

        right_buttons_layout.addWidget(self.sound_button)

        right_buttons_widget.setLayout(right_buttons_layout)

        buttons_layout.addWidget(left_buttons_widget)
        buttons_layout.addWidget(right_buttons_widget)

        buttons_widget.setLayout(buttons_layout)

        sidebar_layout.addWidget(buttons_widget)
        left_sidebar.setLayout(sidebar_layout)
        left_sidebar.setMinimumWidth(250) 
        left_sidebar.setStyleSheet("background-color: lightgray;")

        left_sidebar.setFixedWidth(600)  
        left_sidebar.setFixedHeight(1030)  


        self.media_player = QMediaPlayer()
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile("assets/sirena.wav")))
        self.is_sound_playing = False

        return left_sidebar
    def initialize_sound(self):
        if not hasattr(self, 'pygame_initialized'):
            pygame.mixer.init()
            self.pygame_initialized = True

        pygame.mixer.music.load("assets/sirena.wav")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1) 
        self.is_sound_playing = True
        print("Sonido inicial activado")

    def toggle_sound(self):
        if not hasattr(self, 'pygame_initialized'):
            pygame.mixer.init()
            self.pygame_initialized = True

        if self.is_sound_playing:
            pygame.mixer.music.stop()
            self.sound_button.setIcon(QIcon("assets/sound_off_icon.png"))  
            print("Sonido apagado")
        else:
            pygame.mixer.music.play(-1)
            self.sound_button.setIcon(QIcon("assets/sound_on_icon.png"))  
            print("Sonido encendido")

        self.is_sound_playing = not self.is_sound_playing



    def show_recommendations(self):
        """Mostrar los consejos de sismo."""
        self.recommendations_details.show()

    def hide_recommendations(self):
        """Ocultar los consejos de sismo."""

        self.recommendations_details.hide()

if __name__ == "__main__":
    app = QApplication([]) 
    main_app = MainApp()  
    main_app.show()  
    app.exec() 
