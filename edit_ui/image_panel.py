
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PIL import Image, ImageOps
from edit_ui.image_viewer import ImageViewer
import io

class ImagePanel(QtWidgets.QWidget):
    def __init__(self, width, height, im):
        super().__init__()
        self.layout = QGridLayout()
        self.imageViewer = ImageViewer(im)
        self.fileSelectButton = QPushButton(self)
        self.fileSelectButton.setText("Select Image")
        self.fileTextBox = QLineEdit("Image Path goes here", self)
        self.imgReloadButton = QPushButton(self)
        self.imgReloadButton.setText("Reload image")
        self.xCoordBox = QSpinBox(self)
        self.yCoordBox = QSpinBox(self)
        self.layout.addWidget(self.imageViewer, 0, 0, 1, 14)
        self.layout.addWidget(self.fileSelectButton, 1, 0, 1, 2)
        self.layout.addWidget(self.fileTextBox, 1, 2, 1, 8)
        self.layout.addWidget(self.imgReloadButton, 1, 10, 1, 2)
        self.layout.addWidget(self.xCoordBox, 1, 12, 1, 1)
        self.layout.addWidget(self.yCoordBox, 1, 13, 1, 1)


    def getImage():
        return self.imageViewer.qim

    def getSelection():
        return self.imageViewer.getSelection()
