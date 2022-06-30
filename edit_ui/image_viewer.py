from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PIL import Image
import io

class ImageViewer(QtWidgets.QWidget):

    def __init__(self, im):
        super().__init__()
        self.borderSize = 4
        if im is not None:
            self.loadImage(im)

    def loadImage(self, im):
        self.qim = QtGui.QImage(im.tobytes("raw","RGB"), im.width, im.height, QtGui.QImage.Format_RGB888)
        self.image = QtGui.QPixmap.fromImage(self.qim)
        self.resizeEvent(None)
        if not hasattr(self, 'selected'):
            self.selected = QPoint(0, 0)
        self.update()

    def paintEvent(self, event):
        if not hasattr(self, 'qim'):
            return
        selectionSize = self.scale * 256
        painter = QPainter(self)
        left = (self.width() - self.image.width()) / 2
        top = (self.height() - self.image.height()) / 2
        painter.drawPixmap(QRect(left, top, self.image.width(), self.image.height()), self.image)
        painter.setPen(QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
        if hasattr(self, 'selected'):
            widgetCoords = self.imageToWidgetCoords(self.selected)
            painter.drawRect(widgetCoords.x(), widgetCoords.y(), selectionSize, selectionSize) 

    def imgWidth(self):
        return self.qim.width()

    def imgHeight(self):
        return self.qim.height()

    def imageToWidgetCoords(self, point):
        return QPoint((point.x() * self.scale) + self.xMin, (point.y() * self.scale) + self.yMin)

    def widgetToImageCoords(self, point):
        return QPoint((point.x() - self.xMin) / self.scale, (point.y() - self.yMin) / self.scale)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and hasattr(self, 'qim'):
            imageCoords = self.widgetToImageCoords(event.pos())
            if (imageCoords.x() + 256) > self.qim.width():
                imageCoords.setX(self.qim.width() - 256)
            elif imageCoords.x() < 0:
                imageCoords.setX(0)
            if (imageCoords.y() + 256) > self.qim.height():
                imageCoords.setY(self.qim.height() - 256)
            elif imageCoords.y() < 0:
                imageCoords.setY(0)
            self.selected = imageCoords
            if hasattr(self, 'onSelect'):
                self.onSelect(imageCoords)
            self.update()

    def setSelection(self, pt):
        if (not hasattr(self, 'selected')) or (pt != self.selected):
            self.selected = pt
            self.update()

    def insertIntoSelection(self, image):
        if hasattr(self, 'selected') and hasattr(self, 'qim'):
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            self.qim.save(buffer, "PNG")
            pil_im = Image.open(io.BytesIO(buffer.data()))
            pil_im.paste(image, (self.selected.x(), self.selected.y()))
            self.loadImage(pil_im)

    def getSelection(self):
        if hasattr(self, 'selected'):
            croppedImage = self.qim.copy(self.selected.x(), self.selected.y(), 256, 256)
            buffer = QBuffer()
            buffer.open(QBuffer.ReadWrite)
            croppedImage.save(buffer, "PNG")
            pil_im = Image.open(io.BytesIO(buffer.data()))
            return pil_im

    def resizeEvent(self, event):
        if not hasattr(self, 'qim'):
            return
        imageWidth = self.qim.width()
        imageHeight = self.qim.height()
        widgetWidth = self.width() - (self.borderSize * 2)
        widgetHeight = self.height() - (self.borderSize * 2)
        self.scale = min(widgetWidth/imageWidth, widgetHeight/imageHeight)
        self.xMin = 0
        self.yMin = 0
        if (imageWidth * self.scale) < widgetWidth:
            self.xMin = (widgetWidth - (imageWidth * self.scale)) / 2
        elif (imageHeight * self.scale) < widgetHeight:
            self.yMin = (widgetHeight - (imageHeight * self.scale)) / 2
        self.xMax = self.xMin + (max(0, (imageWidth - 256)) * self.scale)
        self.yMax = self.yMin + (max(0, (imageHeight - 256)) * self.scale)
        #print(f"fitting {imageWidth}x{imageHeight} image in {widgetWidth}x{widgetHeight} container, scaling by {self.scale}")
        self.image = QtGui.QPixmap.fromImage(self.qim)
        self.image = self.image.scaled(imageWidth * self.scale, imageHeight * self.scale)
