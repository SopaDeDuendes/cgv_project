# custom_button.py
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

class CustomButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

        self.setStyleSheet("""
            CustomButton {
                background-color: white;
                border: none;
                border-radius: 10px;
                color: black;
                font-size: 16px;
                padding: 10px;
            }
        """)

        self.set_shadow_effect()

    def set_shadow_effect(self):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(3, 3)
        shadow.setColor(QColor(0, 0, 0, 160))  
        self.setGraphicsEffect(shadow)
        
    def set_expanding(self):
        """ Hacer que el botón se expanda en su layout """
        self.setSizePolicy(Qt.QSizePolicy.Expanding, Qt.QSizePolicy.Expanding)
