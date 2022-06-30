from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt
from edit_ui.mask_creator import MaskCreator

class MaskPanel(QWidget):
    def __init__(self, im, getSelection):
        super().__init__()

        self.maskCreator = MaskCreator(im)
        maskCreator = self.maskCreator

        self.selectMaskAreaButton = QPushButton(self)
        self.selectMaskAreaButton.setText("load selection")
        def applySelection():
            selection = getSelection()
            if selection is not None:
                print('apply selection')
                maskCreator.loadImage(selection)
            else:
                print('selection was None')
        self.selectMaskAreaButton.clicked.connect(applySelection)
        

        self.clearMaskButton = QPushButton(self)
        self.clearMaskButton.setText("clear")

        self.clearMaskButton.clicked.connect(lambda: maskCreator.clear())
        self.maskBrushSizeBox = QSpinBox(self)
        self.maskBrushSizeBox.setToolTip("Brush size")
        self.maskBrushSizeBox.setRange(1, 64)
        self.maskBrushSizeBox.setValue(maskCreator.brushSize)
        self.maskBrushSizeBox.valueChanged.connect(lambda newSize: maskCreator.setBrushSize(newSize))
        

        self.layout = QGridLayout()
        self.borderSize = 4
        def makeSpacer():
            return QSpacerItem(self.borderSize, self.borderSize)
        self.layout.addItem(makeSpacer(), 0, 0, 1, 1)
        self.layout.addItem(makeSpacer(), 3, 0, 1, 1)
        self.layout.addItem(makeSpacer(), 0, 0, 1, 1)
        self.layout.addItem(makeSpacer(), 0, 6, 1, 1)
        self.layout.addWidget(self.maskCreator, 1, 1, 1, 6)
        self.layout.addWidget(self.selectMaskAreaButton, 2, 1, 1, 2)
        self.layout.addWidget(self.clearMaskButton, 2, 3, 1, 2)
        self.layout.addWidget(self.maskBrushSizeBox, 2, 5, 1, 2)
        self.layout.setRowMinimumHeight(1, 300)
        self.setLayout(self.layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, self.borderSize/2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

    def loadImage(self, im):
        self.maskCreator.loadImage(im)

    def getMask(self):
        return self.maskCreator.getMask()
