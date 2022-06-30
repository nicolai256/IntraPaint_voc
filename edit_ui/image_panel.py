from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QPainter, QPen
from PIL import Image
from edit_ui.image_viewer import ImageViewer

class ImagePanel(QWidget):
    def __init__(self, im):
        super().__init__()
        self.imageViewer = ImageViewer(im)
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
        self.imageViewer.onSelect = setCoords

        self.fileTextBox = QLineEdit("Image Path goes here", self)

        def loadImage(filePath):
            try:
                image = Image.open(open(filePath, 'rb')).convert('RGB')
                self.imageViewer.loadImage(image)
                self.fileTextBox.setText(filePath)
                self.xCoordBox.setRange(0, max(image.width - 256, 0))
                self.yCoordBox.setRange(0, max(image.height - 256, 0))
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
        painter.setPen(QPen(Qt.black, self.borderSize/2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

    def getImage(self):
        if hasattr(self.imageViewer, 'qim'):
            return self.imageViewer.qim
        else:
            return None

    def getSelection(self):
        return self.imageViewer.getSelection()
