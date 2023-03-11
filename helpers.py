from PyQt6.QtWidgets import QGraphicsDropShadowEffect


def setShadow(obj, blurradius: int):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blurradius)
    obj.setGraphicsEffect(shadow)