import sys

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtWidgets import QMainWindow, QPushButton

from controllers.volumecontrol import VolumeControl
from helpers import setShadow
from informers.clock import Clock
from informers.networkload import NetworkLoad
from informers.powermonitor import PowerMonitor
from informers.systemload import SystemLoad
from informers.weather import Weather
from launcher.launcher import LaunchButton
from tools import get_config, loadStylesheet, extended_exception_hook


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi('ui/panel.ui', self)
        self.config = get_config("config.toml")
        self.setWindowTitle("QInfoPanel")
        self.exitButton = QPushButton()
        self.exitButton.clicked.connect(self.Exit)
        self.exitButton.setIcon(QIcon.fromTheme("application-exit"))
        self.exitButton.setIconSize(QSize(16, 16))
        self.exitButton.setMaximumSize(16, 16)
        setShadow(self.exitButton, 25)
        self.statusBar.addPermanentWidget(self.exitButton)
        # Window Style
        if self.config['display']['frameless']:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint|Qt.WindowType.Tool|Qt.WindowType.WindowStaysOnBottomHint)
        if self.config['display']['transperent']:
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.setStyleSheet(loadStylesheet("stylesheets/panel.qss"))
        # Informers
        if self.config['weather']['enabled']:
            self.weather = Weather(self)
            self.weather.setMaximumSize(QSize(560, 145))
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

        if self.config['systemload']['enabled']:
            self.systemLoad = SystemLoad()
            self.systemLoad.setMaximumSize(QSize(320, 145))
            self.right_frameLayout.addWidget(self.systemLoad, 0, 0)

        if self.config['networkload']['enabled']:
            self.networkLoad = NetworkLoad()
            self.networkLoad.setMinimumSize(QSize(320, 155))
            self.networkLoad.setMaximumSize(QSize(320, 155))
            self.right_frameLayout.addWidget(self.networkLoad, 1, 0)

        if self.config['volumecontrol']['enabled']:
            self.volumeControl = VolumeControl()
            self.volumeControl.setMaximumSize(QSize(320, 145))
            self.right_frameLayout.addWidget(self.volumeControl, 2, 0)

        if self.config['powermonitor']['enabled']:
            self.powerMon = PowerMonitor()
            self.powerMon.setMaximumSize(QSize(320, 50))
            self.right_frameLayout.addWidget(self.powerMon, 3, 0)

    @staticmethod
    def Exit(self):
        sys.exit(0)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()


    def mouseMoveEvent(self, event):
      self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos )
      self.dragPos = event.globalPosition().toPoint()
      event.accept()

if __name__ == '__main__':
    sys._excepthook = sys.excepthook
    sys.excepthook = extended_exception_hook
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create("fusion"))
    screen_resolution = QGuiApplication.primaryScreen().availableGeometry()
    print(screen_resolution.height(), screen_resolution.width())
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())


