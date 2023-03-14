from datetime import datetime

from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QWidget, QGridLayout, QLabel)

from tools import get_config, loadStylesheet
from helpers import setShadow


class Clock(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stylesheet = "stylesheets/panel.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.config = get_config("config.toml")
        self.clocktimer = QTimer()
        self.clocktimer.timeout.connect(self.Clock)
        self.clocktimer.start(self.config['clock']['refresh_ms'])
        self.layout = QGridLayout()
        self.time_Label = QLabel()
        self.time_Label.setMinimumSize(QSize(0, 0))
        self.time_Label.setMaximumSize(QSize(680, 16777215))
        font = QFont()
        font.setFamily("DSEG14 Classic")
        font.setPointSize(80)
        # font.setBold(True)
        # font.setItalic(False)
        # font.setWeight(75)
        self.time_Label.setFont(font)
        self.time_Label.setStyleSheet("color: " + self.config['clock']['clock_color'] + ";")
        self.time_Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_Label.setObjectName("time_Label")
        self.layout.addWidget(self.time_Label, 0, 5, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)
        setShadow(self.time_Label, 25)

    def Clock(self):
        now = datetime.now()
        current_time = now.strftime(self.config['clock']['time_format'])
        self.time_Label.setText(current_time)  # u'\u2770' + + u'\u2771'
