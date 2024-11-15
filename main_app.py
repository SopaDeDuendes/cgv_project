
from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication  

from buildings.earthquake import EarthquakeSimulator  
from floors.floors_simulation import FloorsSimulation  

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Sismo")
        self.setGeometry(100, 100, 1200, 800)


        main_layout = QHBoxLayout()

        # aside izquierdo 
        self.left_sidebar = self.create_left_sidebar()
        main_layout.addWidget(self.left_sidebar)

        self.central_widget = QStackedWidget()

        # instancia de las Clases

        self.earthquake_view = EarthquakeSimulator() 
        self.simulator_view = FloorsSimulation()  

        self.central_widget.addWidget(self.earthquake_view)
        self.central_widget.addWidget(self.simulator_view)

        self.central_widget.setCurrentWidget(self.earthquake_view)

        main_layout.addWidget(self.central_widget)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_left_sidebar(self):
        left_sidebar = QWidget()
        sidebar_layout = QVBoxLayout()

        title_label = QLabel("Simulador de Sismo")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")
        sidebar_layout.addWidget(title_label)

        start_button = QPushButton("Ver Edificio")
        start_button.clicked.connect(self.switch_to_simulator)
        sidebar_layout.addWidget(start_button)

        back_button = QPushButton("Ver Ciudad")
        back_button.clicked.connect(self.switch_to_earthquake)
        sidebar_layout.addWidget(back_button)

        left_sidebar.setLayout(sidebar_layout)
        left_sidebar.setMinimumWidth(200)
        left_sidebar.setStyleSheet("background-color: lightgray;")

        return left_sidebar

    def switch_to_simulator(self):
        self.central_widget.setCurrentWidget(self.simulator_view)
        
    def switch_to_earthquake(self):
        self.central_widget.setCurrentWidget(self.earthquake_view)

app = QApplication([]) 

main_app = MainApp()
main_app.show()

app.exec()
