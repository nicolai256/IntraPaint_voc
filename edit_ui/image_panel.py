from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QPainter, QPen
from PIL import Image
from edit_ui.image_viewer import ImageViewer

class ImagePanel(QWidget):
    """
    Shows the image being edited, along with associated UI elements.
    ...
    Attributes
    ----------
        imageViewer : ImageViewer
            Main image editing widget
        xCoordBox : QSpinBox
            Connected to the selected inpaiting area's x-coordinate.
        yCoordBox : QSpinBox
            Connected to the selected inpaiting area's y-coordinate.
        fileTextBox : QLineEdit
            Gets/sets the edited image's file path.
        fileSelectButton : QPushButton
            Opens a file selection dialog to load a new image.
        imagReloadButton : QPushButton
            (Re)loads the image from the path in the fileTextBox.
    """

    def __init__(self,
            pilImage=None,
            borderSize=4,
            selectionWidth=256,
            selectionHeight=256):
        """
        Parameters
        ----------
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
        self.imageViewer = ImageViewer(pilImage,
                borderSize,
                selectionWidth,
                selectionHeight)
        imageViewer = self.imageViewer

        # wire x/y coordinate boxes to set selection coordinates:
        self.xCoordBox = QSpinBox(self)
        self.xCoordBox.setToolTip("Selected X coordinate")
        def setX(value):
            if hasattr(imageViewer, 'selected'):
                selection = QPoint(value, imageViewer.selected.y())
                imageViewer.setSelection(selection)
        self.xCoordBox.valueChanged.connect(setX)
        self.yCoordBox = QSpinBox(self)
        self.xCoordBox.setToolTip("Selected Y coordinate")
        def setY(value):
            if hasattr(imageViewer, 'selected'):
                selection = QPoint(imageViewer.selected.x(), value)
                imageViewer.setSelection(selection)
        self.yCoordBox.valueChanged.connect(setY)

        # Update coordinate controls automatically when the selection changes:
        def setCoords(pt):
            self.xCoordBox.setValue(pt.x())
            self.yCoordBox.setValue(pt.y())
        self.imageViewer.onSelection.connect(setCoords)

        self.fileTextBox = QLineEdit("Image Path goes here", self)

        def loadImage(filePath):
            try:
                self.imageViewer.setImage(filePath)
                self.fileTextBox.setText(filePath)
                imageSize = self.imageViewer.imageSize()
                if imageSize:
                    self.xCoordBox.setRange(0, max(
                                imageSize.width() - self.imageViewer.selectionWidth, 0))
                self.yCoordBox.setRange(0, max(
                            imageSize.height() - self.imageViewer.selectionHeight, 0))
            except Exception as err:
                print(f"Failed to load image from '{filePath}': {err}")

        # Set image path, load image viewer when a file is selected:
        self.fileSelectButton = QPushButton(self)
        self.fileSelectButton.setText("Select Image")
        def openImageFile():
            file = QFileDialog.getOpenFileName(self, 'Open Image')
            if file:
                loadImage(file[0])
        self.fileSelectButton.clicked.connect(openImageFile)

        self.imgReloadButton = QPushButton(self)
        self.imgReloadButton.setText("Reload image")
        def reloadImage():
            loadImage(self.fileTextBox.text())
        self.imgReloadButton.clicked.connect(reloadImage)

        self.layout = QGridLayout()
        self.borderSize = 4
        def makeSpacer():
            return QSpacerItem(self.borderSize, self.borderSize)
        self.layout.addItem(makeSpacer(), 0, 0, 1, 1)
        self.layout.addItem(makeSpacer(), 3, 0, 1, 1)
        self.layout.addItem(makeSpacer(), 0, 0, 1, 1)
        self.layout.addItem(makeSpacer(), 0, 6, 1, 1)
        self.layout.addWidget(self.imageViewer, 1, 1, 1, 6)
        self.layout.addWidget(self.fileSelectButton, 2, 1, 1, 1)
        self.layout.addWidget(self.fileTextBox, 2, 2, 1, 1)
        self.layout.addWidget(self.imgReloadButton, 2, 3, 1, 1)
        self.layout.addWidget(self.xCoordBox, 2, 4, 1, 1)
        self.layout.addWidget(self.yCoordBox, 2, 5, 1, 1)
        self.layout.setRowMinimumHeight(1, 300)
        self.layout.setRowMinimumHeight(1, 300)
        self.layout.setColumnStretch(2, 255)
        self.setLayout(self.layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, self.borderSize/2, Qt.SolidLine,
                    Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
