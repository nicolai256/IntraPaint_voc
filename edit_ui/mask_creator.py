from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QPen, QImage
from PyQt5.QtCore import Qt, QPoint, QSize, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PIL import Image
from edit_ui.ui_utils import getScaledPlacement, imageToQImage, qImageToImage, QEqualMargins

class MaskCreator(QtWidgets.QWidget):
    """
    QWidget that shows the selected portion of the edited image, and lets the user draw a mask for inpainting.
    """

    def __init__(self, pilImage):
        """
        Parameters:
        pilImage : Image, optional
            Initial image area selected for editing.
        """
        super().__init__()
        assert pilImage is None or isinstance(pilImage, Image.Image)
        
        self._drawing = False
        self._lastPoint = QPoint()
        self._brushSize = 40
        self._selectionSize = QSize(0, 0)
        self._useEraser=False
        self._canvas = None
        if pilImage is not None:
            self.loadImage(pilImage)

    def selectionWidth(self):
        return self._selectionSize.width()

    def selectionHeight(self):
        return self._selectionSize.height()

    def setSelectionSize(self, size):
        """Set the dimensions(in pixels) of the edited image area."""
        if size != self._selectionSize:
            self._selectionSize = size
            self.resizeEvent(None)

    def setBrushSize(self, newSize):
        self._brushSize = newSize

    def setUseEraser(self, useEraser):
        self._useEraser = useEraser

    def getBrushSize(self):
        return self._brushSize

    def clear(self):
        if self._canvas is not None:
            self._canvas.fill(Qt.transparent)
            self.update()

    def loadImage(self, pilImage):
        if self._canvas is None:
            # Use a canvas that's large enough to look decent even if I add support for editing scaled regions,
            # it'll just get resized to selection size on inpainting anyway.
            canvas_image = QImage(QSize(512, 512), QtGui.QImage.Format_ARGB32)
            self._canvas = QtGui.QPixmap.fromImage(canvas_image)
            self._canvas.fill(Qt.transparent)
        if self._selectionSize != QSize(pilImage.width, pilImage.height):
            self._selectionSize = QSize(pilImage.width, pilImage.height)

        self._imageRect = getScaledPlacement(QRect(QPoint(0, 0), self.size()), self._selectionSize,
                self._borderSize())
        self._qimage = imageToQImage(pilImage)
        self._pixmap = QtGui.QPixmap.fromImage(self._qimage).scaled(self._imageRect.size())
        self.resizeEvent(None)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        if hasattr(self, '_pixmap') and self._pixmap is not None:
            painter.drawPixmap(self._imageRect, self._pixmap)
        if hasattr(self, '_canvas') and self._canvas is not None:
            painter.drawPixmap(self._imageRect, self._canvas)
        painter.drawRect(self._imageRect.marginsAdded(QEqualMargins(self._borderSize())))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drawing = True
            
            self._lastPoint = event.pos() - self._imageRect.topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton and self._drawing and hasattr(self, '_canvas'):
            painter = QPainter(self._canvas)
            if self._useEraser:
                painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.setPen(QPen(Qt.red, self._brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self._lastPoint, event.pos() - self._imageRect.topLeft())
            self._lastPoint = event.pos() - self._imageRect.topLeft()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self._drawing = False

    def getMask(self):
        canvasImage = self._canvas.toImage().scaled(self._selectionSize)
        return qImageToImage(canvasImage)

    def resizeEvent(self, event):
        if self._selectionSize == QSize(0, 0):
            self._imageRect = QRect(0, 0, self.width(), self.height())
        else:
            self._imageRect = getScaledPlacement(QRect(QPoint(0, 0), self.size()), self._selectionSize,
                    self._borderSize())
        if self._canvas:
            self._canvas = self._canvas.scaled(self._imageRect.size())

    def _borderSize(self):
        return (min(self.width(), self.height()) // 40) + 1
