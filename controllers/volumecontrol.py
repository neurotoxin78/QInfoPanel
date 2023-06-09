from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QFrame, QWidget, QHBoxLayout, QLabel, QDial)
from pulsectl import Pulse

from tools import loadStylesheet
from helpers import setShadow


class VolumeControl(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stylesheet = "stylesheets/volumecontrol.qss"
        self.setStyleSheet(loadStylesheet(stylesheet))
        self.volume_frame = QFrame()
        self.volume_frame.setMaximumSize(QSize(16777215, 135))
        # self.volume_frame.setFrameShape(QFrame.StyledPanel)
        # self.volume_frame.setFrameShadow(QFrame.Raised)
        self.volume_frame.setObjectName("volume_frame")
        self.volume_frameLayout = QHBoxLayout(self.volume_frame)
        self.volume_frameLayout.setObjectName("volume_frameLayout")
        self.volume_label = QLabel(self.volume_frame)
        self.volume_label.setMaximumSize(QSize(120, 32))
        font = QFont()
        font.setFamily("DejaVu Sans Mono for Powerline")
        font.setPointSize(18)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(100)
        self.volume_label.setFont(font)
        self.volume_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing |
                                       Qt.AlignmentFlag.AlignVCenter)
        self.volume_label.setObjectName("volume_label")
        self.volume_frameLayout.addWidget(self.volume_label)
        self.volume_dial = QDial()
        self.volume_dial.setMaximumSize(QSize(170, 170))
        self.volume_dial.setObjectName("volume_dial")
        self.volume_frameLayout.addWidget(self.volume_dial)
        setShadow(self.volume_label, 25)
        setShadow(self.volume_dial, 25)
        self.setLayout(self.volume_frameLayout)
        self.volume_dial_set()
        self.volume_dial.valueChanged.connect(self.volume_change)

    def volume_dial_set(self):
        try:
            with Pulse('volume-get-value') as pulse:
                sink_input = pulse.sink_input_list()[0]  # first random sink-input stream
                volume = sink_input.volume
                volume_value = int(volume.value_flat * 100)  # average level across channels (float)
            self.volume_dial.setValue(volume_value)
            self.volume_label.setText(u'\uf027' + str(int(volume_value)) + '%')
        except:
            pass

    def volume_change(self):
        volume_value = self.volume_dial.value() / 100
        # print(volume_val)
        try:
            with Pulse('volume-changer') as pulse:
                sink_input = pulse.sink_input_list()[0]  # first random sink-input stream
                volume = sink_input.volume
                volume.value_flat = volume_value  # sets all volume.values to 0.3
                pulse.volume_set(sink_input, volume)  # applies the change
                self.volume_label.setText(str(int(volume_value * 100)) + '%')
        except:
            pass
