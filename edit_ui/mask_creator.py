from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PIL import Image
from edit_ui.ui_utils import *

class MaskCreator(QtWidgets.QWidget):
    """
    QWidget that shows the selected portion of the edited image, and allows the user to draw a mask for inpainting.
    ...
    Methods
    -------
        setBrushSize : None
            Set the brush size in pixels used when painting the image mask.
        clear : None
            Clear the user-drawn image mask.
        loadImage : None
            Load a new image section for inpainting.
        setUseEraser : None
            Sets whether drawing should add to the mask, or remove from it.
    """

    def __init__(self, pilImage, editWidth=256, editHeight=256, borderSize=6):
        super().__init__()
        self.drawing = False
        self._lastPoint = QPoint()
        self._brushSize = 20
        self._borderSize = borderSize
        self._editWidth=256
        self._editHeight=256
        self._useEraser=False
        canvasImage = QtGui.QImage(editWidth, editHeight, QtGui.QImage.Format_ARGB32)
        self._canvas = QtGui.QPixmap.fromImage(canvasImage)
        self._canvas.fill(Qt.transparent)
        if pilImage is not None:
            self.loadImage(pilImage)

    def setBrushSize(self, newSize):
        self._brushSize = newSize

    def setUseEraser(self, useEraser):
        self._useEraser = useEraser

    def getBrushSize(self):
        return self._brushSize

    def clear(self):
        self._canvas.fill(Qt.transparent)
        self.update()

    def loadImage(self, pilImage):
        displaySize = min(self.width(), self.height()) - self._borderSize * 2
        self._qimage = imageToQImage(pilImage)
        self._pixmap = QtGui.QPixmap.fromImage(self._qimage).scaled(displaySize, displaySize)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        drawRect = QRect(self._imagePt.x(), self._imagePt.y(), self._canvas.width(), self._canvas.height())
        if hasattr(self, '_pixmap'):
            painter.drawPixmap(drawRect, self._pixmap)
        painter.drawPixmap(drawRect, self._canvas)
        painter.drawRect(
                max(self._imagePt.x() - self._borderSize, 0),
                max(self._imagePt.y() - self._borderSize, 0),
                int(self._editWidth * self._scale + self._borderSize * 2),
                int(self._editHeight * self._scale + self._borderSize * 2))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self._lastPoint = event.pos() - self._imagePt

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton and self.drawing and hasattr(self, '_canvas'):
            painter = QPainter(self._canvas)
            if self._useEraser:
                painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.setPen(QPen(Qt.red, self._brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self._lastPoint, event.pos() - self._imagePt)
            self._lastPoint = event.pos() - self._imagePt
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.drawing = False

    def getMask(self):
        canvasImage = self._canvas.toImage().scaled(256, 256)
        return qImageToImage(canvasImage)

    def resizeEvent(self, event):
        self._imagePt, self._scale = getScaledPlacement(
                [self.width(), self.height()],
                [self._editWidth, self._editHeight],
                self._borderSize)
        width = int(self._editWidth * self._scale)
        height = int(self._editHeight * self._scale)
        if hasattr(self, '_pixmap'):
            self._pixmap = self._pixmap.scaled(width, height)
        self._canvas = self._canvas.scaled(width, height)
