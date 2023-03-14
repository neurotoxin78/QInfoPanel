from PyQt6 import uic
from PyQt6.QtCore import Qt, QSize, QProcess, pyqtSlot, QUrl
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QWidget, QCompleter, QFrame, QGridLayout, QPushButton, QVBoxLayout, QHBoxLayout
from tools import get_config, get_apps_list
from helpers import setShadow


class LaunchButton(QWidget):
    def __init__(self, *args, **kwargs):
        super(LaunchButton, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.MainPanel = args[0]
        self.config = get_config("config.toml")
        self.app_config = get_config("launcher.toml")
        self.launcher = Launcher()
        self.process = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
        self.launch_frame = QFrame()
        self.launch_frame.setMinimumSize(QSize(30, 100))
        self.launch_frame.setMaximumSize(QSize(30, 140))
        # self.launch_frame.setFrameShape(QFrame.StyledPanel)
        # self.launch_frame.setFrameShadow(QFrame.Raised)
        self.launch_frame.setObjectName("launch_frame")
        self.launch_frame_frameLayout = QHBoxLayout(self.launch_frame)
        self.launch_frame_frameLayout.setObjectName("launch_frame_frameLayout")
        font = QFont()
        font.setFamily("Roboto Mono for Powerline")
        font.setPointSize(20)
        font.setBold(False)
        font.setUnderline(False)
        font.setWeight(50)
        if self.config['launcher']['enabled']:
            self.launchBtn = QPushButton()
            self.launchBtn.setFont(font)
            self.launchBtn.setIcon(QIcon.fromTheme("applications-other"))
            self.launchBtn.setIconSize(QSize(self.config['launcher']['icon_size'], self.config['launcher']['icon_size']))
            self.launchBtn.setMaximumSize(self.config['launcher']['icon_size'], self.config['launcher']['icon_size'])
            self.launchBtn.clicked.connect(self.launcher.show)
            self.launch_frame_frameLayout.addWidget(self.launchBtn)
            setShadow(self.launchBtn, 25)
            self.c_item = list(self.app_config.keys())

        for i in range(len(self.app_config)):
            config = self.app_config.get(self.c_item[i])
            if config['enabled']:
                button = QPushButton("", self)
                button.setObjectName("shortcut_" + str(i))
                button.setIcon(QIcon.fromTheme(config['icon_name']))
                button.setIconSize(QSize(self.config['launcher']['icon_size'], self.config['launcher']['icon_size']))
                button.setMaximumSize(QSize(self.config['launcher']['icon_size'], self.config['launcher']['icon_size']))
                button.setToolTip(config['tooltip'])
                button.clicked.connect(lambda ch, i=i: self.run(i))      # < ---
                self.launch_frame_frameLayout.addWidget(button)
                setShadow(button, 25)

        self.launcher.lineEdit.returnPressed.connect(lambda: self.AppLaunch(self.launcher.lineEdit.text()))
        self.launcher.launchBtn.clicked.connect(lambda: self.AppLaunch(self.launcher.lineEdit.text()))
        self.setLayout(self.launch_frame_frameLayout)

    def run(self, i):
        config = self.app_config.get(self.c_item[i])
        self.AppLaunch(config['executable_path'])

    def shortcut0_click(self):
        self.AppLaunch(self.app_config['0']['executable_path'])
    def AppLaunch(self, command: str):
        raw_cmd = command.split(sep=" ")
        cmd = raw_cmd[0]
        keys = raw_cmd[1:]
        self.process.start(cmd, keys)
        # self.process.started.connect(lambda: self.MainPanel.showMessage("Виконано", 1500))
        # self.process.finished.connect(lambda: self.MainPanel.showMessage("Закрито", 1500))
        # self.process.error.connect(lambda: self.MainPanel.showMessage("Не виконано", 1500))
        self.launcher.hide()


class Launcher(QWidget):
    def __init__(self, *args, **kwargs):
        super(Launcher, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = get_config("config.toml")
        uic.loadUi('ui/launcher.ui', self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)  # | Qt.WindowModal)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.hideBtn.clicked.connect(self.on_click)
        apps = get_apps_list("/usr/bin")
        self.completer = QCompleter(apps)
        self.lineEdit.setCompleter(self.completer)

    @pyqtSlot()
    def on_click(self):
        self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            print("Enter")


class WebEngine(QWidget):

    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout(self)
        self.webEngineView = QWebEngineView()
        vbox.addWidget(self.webEngineView)
        self.setLayout(vbox)
        # self.setGeometry(300, 300, 350, 250)
        self.loadPage()
        # self.setWindowTitle('QWebEngineView')
        # self.show()

    def loadPage(self):
        self.webEngineView.load(QUrl("http://free-tutorials.org"))
        self.webEngineView.showNormal()

