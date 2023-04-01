from PyQt6.QtCore import Qt, QSize, QCoreApplication, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QFrame, QWidget, QGridLayout, QLabel, QProgressBar, QGraphicsDropShadowEffect)
from tools import loadStylesheet, get_config, get_power_consumption
from helpers import setShadow


class PowerMonitor(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stylesheet = "stylesheets/systemload.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.config = get_config("config.toml")
        self.sensortimer = QTimer()
        self.sensortimer.timeout.connect(self.refresh)
        self.sensortimer.start(self.config['powermonitor']['refresh_ms'])
        self.font = QFont()
        self.font.setFamily("DejaVu Sans Mono for Powerline")
        self.font.setPointSize(12)
        self.font.setBold(True)
        self.font.setUnderline(False)
        self.font.setWeight(100)
        self.sensor_frame = QFrame()
        self.sensor_frame.setMinimumSize(QSize(0, 150))
        self.sensor_frame.setMaximumSize(QSize(16777215, 150))
        self.sensor_frame.setStyleSheet("background-color: rgba(85, 85, 127, 160);")
        self.sensor_frame.setObjectName("sensor_frame")
        self.sensor_frameLayout = QGridLayout(self.sensor_frame)
        self.sensor_frameLayout.setObjectName("sensor_frameLayout")
        self.setLayout(self.sensor_frameLayout)
        self.make_source_labels()
        self.make_voltage_labels()
        self.make_current_labels()
        self.make_power_labels()


    def make_power_labels(self):
        self.power_sbc = QLabel()
        self.power_sbc.setFont(self.font)
        self.power_sbc.setMinimumSize(QSize(39, 39))
        self.power_sbc.setObjectName("power_sbc")
        self.sensor_frameLayout.addWidget(self.power_sbc, 0, 4, 1, 1)
        self.power_usb = QLabel()
        self.power_usb.setFont(self.font)
        self.power_usb.setMinimumSize(QSize(39, 39))
        self.power_usb.setObjectName("power_usb")
        self.sensor_frameLayout.addWidget(self.power_usb, 1, 4, 1, 1)
        self.power_clr = QLabel()
        self.power_clr.setFont(self.font)
        self.power_clr.setMinimumSize(QSize(39, 39))
        self.power_clr.setObjectName("power_usb")
        self.sensor_frameLayout.addWidget(self.power_clr, 2, 4, 1, 1)
        setShadow(self.power_sbc, 20)
        setShadow(self.power_usb, 20)
        setShadow(self.power_clr, 20)

    def make_current_labels(self):
        self.current_sbc = QLabel()
        self.current_sbc.setFont(self.font)
        self.current_sbc.setMinimumSize(QSize(39, 39))
        self.current_sbc.setObjectName("current_sbc")
        self.sensor_frameLayout.addWidget(self.current_sbc, 0, 3, 1, 1)
        self.current_usb = QLabel()
        self.current_usb.setFont(self.font)
        self.current_usb.setMinimumSize(QSize(39, 39))
        self.current_usb.setObjectName("current_usb")
        self.sensor_frameLayout.addWidget(self.current_usb, 1, 3, 1, 1)
        self.current_clr = QLabel()
        self.current_clr.setFont(self.font)
        self.current_clr.setMinimumSize(QSize(39, 39))
        self.current_clr.setObjectName("current_usb")
        self.sensor_frameLayout.addWidget(self.current_clr, 2, 3, 1, 1)
        setShadow(self.current_sbc, 20)
        setShadow(self.current_usb, 20)
        setShadow(self.current_clr, 20)

    def make_voltage_labels(self):
        self.voltage_sbc = QLabel()
        self.voltage_sbc.setFont(self.font)
        self.voltage_sbc.setMinimumSize(QSize(39, 39))
        self.voltage_sbc.setObjectName("voltage_sbc")
        self.sensor_frameLayout.addWidget(self.voltage_sbc, 0, 2, 1, 1)
        self.voltage_usb = QLabel()
        self.voltage_usb.setFont(self.font)
        self.voltage_usb.setMinimumSize(QSize(39, 39))
        self.voltage_usb.setObjectName("voltage_usb")
        self.sensor_frameLayout.addWidget(self.voltage_usb, 1, 2, 1, 1)
        self.voltage_clr = QLabel()
        self.voltage_clr.setFont(self.font)
        self.voltage_clr.setMinimumSize(QSize(39, 39))
        self.voltage_clr.setObjectName("voltage_usb")
        self.sensor_frameLayout.addWidget(self.voltage_clr, 2, 2, 1, 1)
        setShadow(self.voltage_sbc, 20)
        setShadow(self.voltage_usb, 20)
        setShadow(self.voltage_clr, 20)

    def make_source_labels(self):
        self.source_label_sbc = QLabel()
        self.source_label_sbc.setFont(self.font)
        self.source_label_sbc.setMinimumSize(QSize(39, 39))
        self.source_label_sbc.setObjectName("source")
        self.source_label_sbc.setText("SBC : ")
        self.sensor_frameLayout.addWidget(self.source_label_sbc, 0, 1, 1, 1)
        self.source_label_usb = QLabel()
        self.source_label_usb.setFont(self.font)
        self.source_label_usb.setMinimumSize(QSize(39, 39))
        self.source_label_usb.setObjectName("source")
        self.source_label_usb.setText("USB : ")
        self.sensor_frameLayout.addWidget(self.source_label_usb, 1, 1, 1, 1)
        self.source_label_clr = QLabel()
        self.source_label_clr.setFont(self.font)
        self.source_label_clr.setMinimumSize(QSize(39, 39))
        self.source_label_clr.setObjectName("source")
        self.source_label_clr.setText("CLR : ")
        self.sensor_frameLayout.addWidget(self.source_label_clr, 2, 1, 1, 1)
        setShadow(self.source_label_sbc, 20)
        setShadow(self.source_label_usb, 20)
        setShadow(self.source_label_clr, 20)

    def refresh(self):
        sbc_voltage = get_power_consumption(self.config['powermonitor']['sbc_voltage_sensor']) / 1000
        sbc_current = get_power_consumption(self.config['powermonitor']['sbc_current_sensor']) / 10
        usb_voltage = get_power_consumption(self.config['powermonitor']['usb_voltage_sensor']) / 1000
        usb_current = get_power_consumption(self.config['powermonitor']['usb_current_sensor']) / 10
        clr_voltage = get_power_consumption(self.config['powermonitor']['clr_voltage_sensor']) / 1000
        clr_current = get_power_consumption(self.config['powermonitor']['clr_current_sensor']) / 10
        watt_sbc = "%.1f" % sbc_voltage
        self.voltage_sbc.setText(watt_sbc + "V")
        volt_usb = "%.1f" % usb_voltage
        self.voltage_usb.setText(volt_usb + "V")
        volt_clr = "%.1f" % clr_voltage
        self.voltage_clr.setText(volt_clr + "V")
        current_sbc = "%.0f" % sbc_current
        self.current_sbc.setText(current_sbc + "mA")
        current_usb = "%.0f" % usb_current
        self.current_usb.setText(current_usb + "mA")
        current_clr = "%.0f" % clr_current
        self.current_clr.setText(current_clr + "mA")
        power_sbc = (sbc_voltage * sbc_current)  / 1000
        watt_sbc = "%.1f" % power_sbc
        self.power_sbc.setText(watt_sbc + "W")
        power_usb = (usb_voltage * usb_current)  / 1000
        watt_usb = "%.1f" % power_usb
        self.power_usb.setText(watt_usb + "W")
        power_clr = (clr_voltage * clr_current)  / 1000
        watt_clr = "%.1f" % power_clr
        self.power_clr.setText(watt_clr + "W")