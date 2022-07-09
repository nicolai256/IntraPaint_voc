from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
import PyQt5.QtGui as QtGui
from PIL import Image
from edit_ui.ui_utils import *

class ImageViewer(QtWidgets.QWidget):
    """
    QWidget that shows the image being edited, and allows the user to select sections.
    ...
    Attributes:
    -----------
    selectionWidth : int
        Width in pixels of any selected image section.
    selectionHeight : int
        Height in pixels of any selected image section.
    onSelection : pyqtSignal(QPoint)
        Signal that fires whenever the selection changes coordinates, or whenever the image portion under the
        selection changes.

    Methods:
    --------
    getImage : Image
        Gets the widget's image.
    setImage : None
        Applies a new image to the widget.
    getSelection : QPoint
        Gets the coordinates of the selected image section.
    setSelection : None
        Sets the coordinates of the image that should be selected.
    insertIntoSelection : None
        Paste an image sample over the current image at the selection coordinates.
    getSelectedSection : Image
        Returns the selected portion of the image.
    """
    onSelection = pyqtSignal(QPoint)

    def __init__( self,
            pilImage=None,
            borderSize=4,
            selectionWidth=256,
            selectionHeight=256):
        """
        Parameters:
        -----------
        pilImage : Image, optional
            An initial pillow Image object to load.
        borderSize : int, optional
            Width in pixels of the border around the image.
        selectionWidth : int, optional
            Width in pixels of selected image sections used for inpainting.
            Values greater than 256 will probably not work well.
        selectionHeight : int, optional
            Height in pixels of selected image sections used for inpainting.
            Values greater than 256 will probably not work well.
        """
        super().__init__()
        self.selectionWidth = selectionWidth
        self.selectionHeight = selectionHeight
        self._borderSize = borderSize
        self.selectionWidth = selectionWidth
        if pilImage is not None:
            self.setImage(pilImage)

    def getImage(self):
        """Returns the image currently being edited as a PIL Image object"""
        return qImageToImage(self._qimage)

    def setImage(self, pilImage):
        """Applies a pillow Image object as the new image to be edited."""
        self._qimage = imageToQImage(pilImage)
        if self._qimage is None:
            print("ImageViewer.setImage: invalid PIL image!")
            return
        self._pixmap = QtGui.QPixmap.fromImage(self._qimage)
        self.resizeEvent(None)
        if not hasattr(self, 'selected'):
            self.selected = QPoint(0, 0)
        self.onSelection.emit(self.selected)
        self.update()

    def getSelection(self):
        """Gets the QPoint coordinates of the area selected for inpainting."""
        if hasattr(self, 'selected'):
            return self.selected

    def setSelection(self, pt):
        """Sets the QPoint coordinates of the area selected for inpainting."""

        # Unless selection size exceeds image size, ensure the selection is
        # entirely within the image:
        if pt.x() >= (self._qimage.width() - self.selectionWidth):
            pt.setX(self._qimage.width() - self.selectionWidth - 1)
        if pt.x() < 0:
            pt.setX(0)
        if pt.y() >= (self._qimage.height() - self.selectionHeight):
            pt.setY(self._qimage.height() - self.selectionHeight - 1)
        if pt.y() < 0:
            pt.setY(0)
        if (not hasattr(self, 'selected')) or (pt != self.selected):
            self.selected = pt
            self.onSelection.emit(self.selected)
            self.update()

    def insertIntoSelection(self, image):
        """Pastes a pillow image object onto the image at the selected coordinates."""
        if hasattr(self, 'selected') and hasattr(self, '_qimage'):
            pilImage = qImageToImage(self._qimage)
            pilImage.paste(image, (self.selected.x(), self.selected.y()))
            self.setImage(pilImage)

    def getSelectedSection(self):
        """Gets a copy of the image, cropped to the current selection area."""
        if hasattr(self, 'selected'):
            croppedImage = self._qimage.copy(self.selected.x(),
                    self.selected.y(),
                    self.selectionWidth,
                    self.selectionHeight)
            return qImageToImage(croppedImage)

    def _imageToWidgetCoords(self, point):
        return QPoint(int(point.x() * self._scale) + self._xMin,
                int(point.y() * self._scale) + self._yMin)

    def _widgetToImageCoords(self, point):
        return QPoint(int((point.x() - self._xMin) / self._scale),
                int((point.y() - self._yMin) / self._scale))

    def paintEvent(self, event):
        if not hasattr(self, '_qimage'):
            return
        painter = QPainter(self)
        left = (self.width() - self._pixmap.width()) // 2
        top = (self.height() - self._pixmap.height()) // 2
        painter.drawPixmap(QRect(left, top, self._pixmap.width(), self._pixmap.height()), self._pixmap)

        painter.setPen(QPen(Qt.black, self._borderSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
        if hasattr(self, 'selected'):
            painter.setPen(QPen(Qt.black, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            widgetCoords = self._imageToWidgetCoords(self.selected)
            painter.drawRect(
                    widgetCoords.x(),
                    widgetCoords.y(),
                    int(self.selectionWidth * self._scale),
                    int(self.selectionHeight * self._scale)) 

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and hasattr(self, '_qimage'):
            imageCoords = self._widgetToImageCoords(event.pos())
            self.setSelection(imageCoords)
            self.update()

    def resizeEvent(self, event):
        if not hasattr(self, '_qimage'):
            return
        imageWidth = self._qimage.width()
        imageHeight = self._qimage.height()
        imagePt, self._scale = getScaledPlacement(
                [self.width(), self.height()],
                [imageWidth, imageHeight],
                self._borderSize)
        self._xMin = imagePt.x()
        self._yMin = imagePt.y()
        self._xMax = self._xMin + int(imageWidth * self._scale)
        self._yMax = self._yMin + int(imageHeight * self._scale)
        self._pixmap = QtGui.QPixmap.fromImage(self._qimage)
        self._pixmap = self._pixmap.scaled(int(imageWidth * self._scale), int(imageHeight * self._scale))
