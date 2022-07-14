from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QPainter, QPen
from PIL import Image, ImageOps
import io

class InpaintingPanel(QWidget):
    def __init__(self, doInpaint, getImage, getSelection, getMask):
        super().__init__()
        assert callable(doInpaint)
        assert callable(getImage)
        assert callable(getSelection)
        assert callable(getMask)

        self.textPromptBox = QLineEdit("", self)

        self.batchSizeBox = QSpinBox(self)
        self.batchSizeBox.setValue(3)
        self.batchSizeBox.setRange(1, 9)
        self.batchSizeBox.setToolTip("Batch Size")
        self.batchCountBox = QSpinBox(self)
        self.batchCountBox.setValue(3)
        self.batchCountBox.setRange(1, 9)
        self.batchCountBox.setToolTip("Batch Count")

        self.inpaintButton = QPushButton();
        self.inpaintButton.setText("Start inpainting")
        self.inpaintButton.clicked.connect(lambda: doInpaint( getSelection(), \
                    getMask(), \
                    self.textPromptBox.text(), \
                    self.batchSizeBox.value(), \
                    self.batchCountBox.value()))

        def saveImage():
            file = QFileDialog.getSaveFileName(self, 'Save Image')
            image = getImage()
            try:
                if file and file[1] and (image is not None):
                    file = file[0]
                    image.save(file, "PNG")
            except Exception as err:
                print(f"Saving image failed: {err}")
        self.saveButton = QPushButton(self)
        self.saveButton.clicked.connect(saveImage)
        self.saveButton.setText("Save Image")

        self.layout = QGridLayout()
        # Row 1:
        self.layout.addWidget(QLabel(self, text="Prompt"), 1, 1, 1, 1)
        self.layout.addWidget(self.textPromptBox, 1, 2, 1, 1)
        self.layout.addWidget(QLabel(self, text="Batch size:"), 1, 3, 1, 1)
        self.layout.addWidget(self.batchSizeBox, 1, 4, 1, 1)
        self.layout.addWidget(QLabel(self, text="Batch count:"), 1, 5, 1, 1)
        self.layout.addWidget(self.batchCountBox, 1, 6, 1, 1)
        self.layout.addWidget(self.inpaintButton, 1, 7, 1, 1)
        self.layout.addWidget(self.saveButton, 1, 8, 1, 1)
        self.layout.setColumnStretch(2, 255) # Maximize prompt input
        self.setLayout(self.layout)
