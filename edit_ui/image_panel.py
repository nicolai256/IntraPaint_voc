from PyQt5.QtWidgets import QWidget, QSpinBox, QLineEdit, QPushButton, QLabel, QGridLayout, QSpacerItem, QFileDialog
from PyQt5.QtCore import Qt, QPoint, QSize, QRect, QBuffer
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

    def __init__(self, pilImage=None, selectionSize=QSize(256, 256)):
        """
        Parameters
        ----------
        pilImage : Image, optional
            An initial pillow Image object to load.
        selectionSize : QSize, default QSize(256, 256)
            Size in pixels of selected image sections used for inpainting.
            Dimensions should be positive multiples of 64, no greater than 256.
        """
        super().__init__()
        assert pilImage is None or isinstance(pilImage, Image.Image)
        assert isinstance(selectionSize, QSize)

        self.imageViewer = ImageViewer(pilImage, selectionSize)
        imageViewer = self.imageViewer

        # wire x/y coordinate boxes to set selection coordinates:
        self.xCoordBox = QSpinBox(self)
        self.yCoordBox = QSpinBox(self)
        self.xCoordBox.setToolTip("Selected X coordinate")
        def setX(value):
            lastSelected = imageViewer.getSelection()
            if lastSelected:
                selection = QPoint(value, lastSelected.y())
                imageViewer.setSelection(selection)
        self.xCoordBox.valueChanged.connect(setX)
        self.xCoordBox.setToolTip("Selected Y coordinate")
        def setY(value):
            lastSelected = imageViewer.getSelection()
            if lastSelected:
                selection = QPoint(lastSelected.x(), value)
                imageViewer.setSelection(selection)
        self.yCoordBox.valueChanged.connect(setY)

        # Selection size controls:
        self.widthBox = QSpinBox(self)
        self.heightBox = QSpinBox(self)
        for sizeControl, typeName in [(self.widthBox, "width"), (self.heightBox, "height")]:
            sizeControl.setToolTip(f"Selected area {typeName}")
            sizeControl.setRange(64, 256)
            sizeControl.setSingleStep(64)
            sizeControl.setValue(256)
        def setW(value):
            size = QSize(value, imageViewer.selectionHeight())
            imageSize = self.imageViewer.imageSize()
            if imageSize:
                self.xCoordBox.setMaximum(imageSize.width() - value)
            imageViewer.setSelection(size=size)
        self.widthBox.valueChanged.connect(setW)
        def setH(value):
            size = QSize(imageViewer.selectionWidth(), value)
            imageSize = self.imageViewer.imageSize()
            if imageSize:
                self.yCoordBox.setMaximum(imageSize.height() - value)
            imageViewer.setSelection(size=size)
        self.heightBox.valueChanged.connect(setH)

        # Update coordinate controls automatically when the selection changes:
        def setCoords(pt, size):
            self.xCoordBox.setValue(pt.x())
            self.yCoordBox.setValue(pt.y())
            self.widthBox.setValue(size.width())
            self.heightBox.setValue(size.height())
        self.imageViewer.onSelection.connect(setCoords)

        self.fileTextBox = QLineEdit("", self)


        # Set image path, load image viewer when a file is selected:
        self.fileSelectButton = QPushButton(self)
        self.fileSelectButton.setText("Select Image")
        def openImageFile():
            file, fileSelected = QFileDialog.getOpenFileName(self, 'Open Image')
            if file and fileSelected:
                self.loadImage(file)
        self.fileSelectButton.clicked.connect(openImageFile)

        self.imgReloadButton = QPushButton(self)
        self.imgReloadButton.setText("Reload image")
        def reloadImage():
            self.loadImage(self.fileTextBox.text())
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
        self.layout.addWidget(QLabel(self, text="Image path:"), 2, 2, 1, 1)
        self.layout.addWidget(self.fileTextBox, 2, 3, 1, 1)
        self.layout.addWidget(self.imgReloadButton, 2, 4, 1, 1)

        self.layout.addWidget(QLabel(self, text="X:"), 2, 5, 1, 1)
        self.layout.addWidget(self.xCoordBox, 2, 6, 1, 1)
        self.layout.addWidget(QLabel(self, text="Y:"), 2, 7, 1, 1)
        self.layout.addWidget(self.yCoordBox, 2, 8, 1, 1)

        self.layout.addWidget(QLabel(self, text="W:"), 3, 5, 1, 1)
        self.layout.addWidget(self.widthBox, 3, 6, 1, 1)
        self.layout.addWidget(QLabel(self, text="H:"), 3, 7, 1, 1)
        self.layout.addWidget(self.heightBox, 3, 8, 1, 1)

        self.layout.setRowMinimumHeight(1, 300)
        self.layout.setRowMinimumHeight(1, 300)
        self.layout.setColumnStretch(3, 255)
        self.setLayout(self.layout)

    def loadImage(self, filePath):
        try:
            self.imageViewer.setImage(filePath)
            self.fileTextBox.setText(filePath)
            imageSize = self.imageViewer.imageSize()
            if imageSize:
                if imageSize.width() < 64 or imageSize.height() < 64:
                    raise Exception(f"image width and height must be no smaller than 64px, got {imageSize}")
                self.xCoordBox.setRange(0, max(
                            imageSize.width() - self.imageViewer.selectionWidth(), 0))
                self.yCoordBox.setRange(0, max(
                            imageSize.height() - self.imageViewer.selectionHeight(), 0))
                self.widthBox.setMaximum(min(256, imageSize.width() - (imageSize.width() % 64)))
                self.heightBox.setMaximum(min(256, imageSize.height() - (imageSize.height() % 64)))
        except Exception as err:
            print(f"Failed to load image from '{filePath}': {err}")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, self.borderSize/2, Qt.SolidLine,
                    Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)
