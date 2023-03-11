import sys

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow

from informers.clock import Clock
from informers.weather import Weather
from launcher.launcher import LaunchButton
from tools import get_config, loadStylesheet, extended_exception_hook


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('ui/panel.ui', self)
        self.config = get_config()
        self.setWindowTitle("QInfoPanel")
        # self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        # | Qt.WindowType.WindowStaysOnBottomHint)
        # self.setAttribute(Qt.WA_NoSystemBackground, True)
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setStyleSheet(loadStylesheet("stylesheets/panel.qss"))
        # Informers
        if self.config['weather']['enabled']:
            self.weather = Weather(self)
            self.weather.setMaximumSize(QSize(600, 145))
            self.left_frameLayout.addWidget(self.weather, 0, 0)
            try:
                self.weather.get_weather()
            except:
                pass
        if self.config['clock']['enabled']:
            self.clock = Clock()
            self.clock.setMaximumSize(QSize(600, 145))
            self.left_frameLayout.addWidget(self.clock, 1, 0)

        if self.config['launcher']['enabled']:
            self.launchButton = LaunchButton(self)
            self.left_frameLayout.addWidget(self.launchButton, 2, 0, 1, 1)


if __name__ == '__main__':
    sys._excepthook = sys.excepthook
    sys.excepthook = extended_exception_hook
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create("fusion"))
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


