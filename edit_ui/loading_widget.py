from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QMargins

class LoadingWidget(QWidget):
    """Show a loading indicator while waiting for samples to load:"""
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        painter = QPainter(self)
        margins = QMargins(self.width() // 3, self.height() // 3, self.width() // 3, self.height() // 3)
        loadingBox = self.frameGeometry().marginsRemoved(margins)
        painter.fillRect(loadingBox, QColor(0, 0, 0, 200))
        painter.setPen(QPen(Qt.white, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawText(self.width() // 2 - 20, self.height() // 2, "Loading...")
