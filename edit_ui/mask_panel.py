from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt
from PIL import Image
from edit_ui.mask_creator import MaskCreator

class MaskPanel(QWidget):
    def __init__(self, pilImage, getSelection, selectionChangeSignal):
        super().__init__()
        assert pilImage is None or isinstance(pilImage, Image.Image)
        assert callable(getSelection)
        assert hasattr(selectionChangeSignal, 'connect') and callable(selectionChangeSignal.connect)

        self.maskCreator = MaskCreator(pilImage)

        maskCreator = self.maskCreator
        def applySelection(pt, size):
            if size is not None:
                maskCreator.setSelectionSize(size)
            selection = getSelection()
            if selection is not None:
                maskCreator.loadImage(selection)
            maskCreator.update()
        selectionChangeSignal.connect(applySelection)


        self.maskBrushSizeBox = QSpinBox(self)
        self.maskBrushSizeBox.setToolTip("Brush size")
        self.maskBrushSizeBox.setRange(1, 200)
        self.maskBrushSizeBox.setValue(maskCreator.getBrushSize())
        self.maskBrushSizeBox.valueChanged.connect(lambda newSize: maskCreator.setBrushSize(newSize))

        self.eraserCheckbox = QCheckBox(self)
        self.eraserCheckbox.setText("Use eraser")
        self.eraserCheckbox.setChecked(False)
        def toggleEraser():
            self.maskCreator.setUseEraser(self.eraserCheckbox.isChecked())
        self.eraserCheckbox.stateChanged.connect(toggleEraser)

        self.clearMaskButton = QPushButton(self)
        self.clearMaskButton.setText("clear")
        def clearMask():
            self.maskCreator.clear()
            self.eraserCheckbox.setChecked(False)
        self.clearMaskButton.clicked.connect(clearMask)

        self.layout = QGridLayout()
        self.borderSize = 4
        def makeSpacer():
            return QSpacerItem(self.borderSize, self.borderSize)
        self.layout.addItem(makeSpacer(), 0, 0, 1, 1)
        self.layout.addItem(makeSpacer(), 3, 0, 1, 1)
        self.layout.addItem(makeSpacer(), 0, 0, 1, 1)
        self.layout.addItem(makeSpacer(), 0, 6, 1, 1)
        self.layout.addWidget(self.maskCreator, 1, 1, 1, 6)
        self.layout.addWidget(QLabel(self, text="Brush size:"), 2, 1, 1, 1)
        self.layout.addWidget(self.maskBrushSizeBox, 2, 2, 1, 1)
        self.layout.addWidget(self.eraserCheckbox, 2, 3, 1, 1)
        self.layout.addWidget(self.clearMaskButton, 2, 4, 1, 2)
        self.layout.setRowMinimumHeight(1, 300)
        self.setLayout(self.layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, self.borderSize//2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

    def loadImage(self, im):
        self.maskCreator.loadImage(im)

    def getMask(self):
        return self.maskCreator.getMask()

    def resizeEvent(self, event):
        # Force MaskCreator aspect ratio to match edit sizes, while leaving room for controls:
        creatorWidth = self.maskCreator.width()
        creatorHeight = creatorWidth
        if self.maskCreator.selectionWidth() > 0:
            creatorHeight = creatorWidth * self.maskCreator.selectionHeight() // self.maskCreator.selectionWidth()
        maxHeight = self.clearMaskButton.y() - self.borderSize
        if creatorHeight > maxHeight:
            creatorHeight = maxHeight
            creatorWidth = creatorHeight * self.maskCreator.selectionWidth() // self.maskCreator.selectionHeight()
        if creatorHeight != self.maskCreator.height() or creatorWidth != self.maskCreator.width():
            x = (self.width() - self.borderSize - creatorWidth) // 2
            y = self.borderSize + (maxHeight - creatorHeight) // 2
            self.maskCreator.setGeometry(x, y, creatorWidth, creatorHeight)
