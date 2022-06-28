from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PIL import Image, ImageOps
import io

class ImageViewer(QtWidgets.QWidget):

    def __init__(self, im):
        super().__init__()
        self.qim = QtGui.QImage(im.tobytes("raw","RGB"), im.width, im.height, QtGui.QImage.Format_RGB888)
        self.image = QtGui.QPixmap.fromImage(self.qim)
        self.selection = False

    def loadImage(self, im):
        self.qim = QtGui.QImage(im.tobytes("raw","RGB"), im.width, im.height, QtGui.QImage.Format_RGB888)
        self.image = QtGui.QPixmap.fromImage(self.qim)
        self.update()

    def paintEvent(self, event):
        selectionSize = self.scale * 256
        painter = QPainter(self)
        left = (self.width() - self.image.width()) / 2
        top = (self.height() - self.image.height()) / 2
        painter.drawPixmap(QRect(left, top, self.image.width(), self.image.height()), self.image)
        if self.selection:
            painter.setPen(QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawRect(self.selected.x(), self.selected.y(), selectionSize, selectionSize) 

    def imgWidth(self):
        return self.qim.width()

    def imgHeight(self):
        return self.qim.height()

    def imageToWidgetCoords(self, point):
        return QPoint((point.x() * self.scale) + self.xMin, (point.y() * self.scale) + self.yMin)

    def widgetToImageCoords(self, point):
        return QPoint((point.x() - self.xMin) / self.scale), (point.y() - self.yMin) / self.scale)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            imageCoords = self.widgetToImageCoords(event.pos())
            left = (self.width() - self.image.width()) / 2
            top = (self.height() - self.image.height()) / 2
            right = self.image.width() - left
            bottom = self.image.height() - top
            selectionSize = self.scale * 256

            self.selection = True
            self.selected = event.pos()
            print(f"l={left},r={right},t={top},b={bottom},s={self.scale}")
            if (self.selected.x() + selectionSize) > right:
                self.selected.setX(right - selectionSize)
            if self.selected.x() < left:
                self.selected.setX(left)
            if (self.selected.y() + selectionSize) > bottom:
                self.selected.setY(bottom - selectionSize)
            if self.selected.y() < top:
                self.selected.setY(bottom - selectionSize)
            print(f"selected: {self.selected.x()},{self.selected.y()}")
            self.update()


    def getSelection(self):
        if self.selection:
            left = (self.width() - self.image.width()) / 2
            top = (self.height() - self.image.height()) / 2
            croppedImage = self.qim.copy((self.selected.x() - left) * self.scale, (self.selected.y() - top) * self.scale, 256, 256)
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            croppedImage.save(buffer, "PNG")
            pil_im = Image.open(io.BytesIO(buffer.data()))
            return pil_im

    def resizeEvent(self, event):
        imageWidth = self.qim.width()
        imageHeight = self.qim.height()
        widgetWidth = self.width()
        widgetHeight = self.height()
        self.xMin = 0
        self.yMin = 0
        if (imageWidth * scale) < widgetWidth:
            self.xMin = (widgetWidth - (imageWidth * scale)) / 2
        elif (imageHeight * scale) < widgetHeight:
            self.yMin = (widgetHeight - (imageHeight * scale)) / 2
        self.image = QtGui.QPixmap.fromImage(self.qim)
        self.scale = min(imageWidth/widgetWidth, imageHeight/widgetHeight)
        self.image = self.image.scaled(imageWidth * self.scale, imageHeight * self.scale)
