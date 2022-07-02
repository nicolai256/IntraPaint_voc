from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PIL import Image, ImageOps
import io

class MaskCreator(QtWidgets.QWidget):

    def __init__(self, im):
        super().__init__()
        self.drawing = False
        self.lastPoint = QPoint()
        self.brushSize = 20
        self.borderSize = 6
        if im is not None:
            self.loadImage(im)

    def setBrushSize(self, newSize):
        self.brushSize = newSize

    def clear(self):
        if hasattr(self, 'canvas'):
            self.canvas.fill(Qt.transparent)
            self.update()

    def loadImage(self, im):
        if hasattr(self, 'im'):
            self.qim = None
            self.image = None
            self.canvas = None
        else:
            displaySize = min(self.width(), self.height()) - self.borderSize * 2
            self.qim = QtGui.QImage(im.tobytes("raw","RGB"), im.width, im.height, QtGui.QImage.Format_RGB888)
            self.image = QtGui.QPixmap.fromImage(self.qim).scaled(displaySize, displaySize)
            canvas = QtGui.QImage(self.image.width(), self.image.height(), QtGui.QImage.Format_ARGB32)
            self.canvas = QtGui.QPixmap.fromImage(canvas)
            self.canvas.fill(Qt.transparent)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        if hasattr(self, 'image'):
            painter.drawPixmap(QRect(self.borderSize, self.borderSize, self.image.width(), self.image.height()), self.image)
            painter.drawPixmap(QRect(self.borderSize, self.borderSize, self.canvas.width(), self.canvas.height()), self.canvas)
            painter.drawRect(self.borderSize / 2, self.borderSize / 2, self.image.width() + self.borderSize, self.image.height() + self.borderSize)
        else:
            painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton and self.drawing and hasattr(self, 'canvas'):
            painter = QPainter(self.canvas)
            painter.setPen(QPen(Qt.red, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.drawing = False

    def getMask(self):
        if hasattr(self, 'canvas'):
            image = self.canvas.toImage().scaled(256, 256)
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            image.save(buffer, "PNG")
            pil_im = Image.open(io.BytesIO(buffer.data()))
            return pil_im
        else:
            print("Warning: no mask found")

    def resizeEvent(self, event):
        if hasattr(self, 'image'):
            displaySize = min(self.width(), self.height()) - self.borderSize * 2
            self.image = QtGui.QPixmap.fromImage(self.qim)
            self.image = self.image.scaled(displaySize, displaySize)

            canvas = QtGui.QImage(self.image.width(), self.image.height(), QtGui.QImage.Format_ARGB32)
            self.canvas = QtGui.QPixmap.fromImage(canvas)
            self.canvas.fill(Qt.transparent)
