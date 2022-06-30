from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer

class LoadingWidget(QWidget):
    def __init__(self):
        super().__init__()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        minDim = min(self.width(), self.height())
        left = (self.width() - minDim) / 2
        top = (self.height() - minDim) / 2
        painter.fillRect(left, top, minDim, minDim, Qt.black)
        painter.setPen(QPen(Qt.white, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawText(left + (minDim / 10), self.height() / 2, "Loading...")

class SampleSelector(QWidget):

    def __init__(self, width, height, batch_size, num_batches, applySample, closeSelector):
        super().__init__()
        self.applySample = applySample
        self.samples = []
        self.selected = None

        instructions = QLabel(self)
        instructions.setText("Click a sample to apply it to the source image, or click 'cancel' to discard all samples.")

        self.cancelButton = QPushButton(self)
        self.cancelButton.setText("cancel")
        self.cancelButton.clicked.connect(closeSelector)

        
        self.layout = QVBoxLayout()
        self.topBarLayout = QHBoxLayout()
        self.gridLayout = QGridLayout()
        self.layout.addLayout(self.topBarLayout, 10)
        self.layout.addLayout(self.gridLayout, 200)

        self.topBarLayout.addWidget(instructions, 10)
        self.topBarLayout.addWidget(self.cancelButton, 1)
        for column in range(batch_size):
            self.gridLayout.setColumnMinimumWidth(column, min(256, self.width() / batch_size))

        for row in range(num_batches):
            for column in range(batch_size):
                sample = LoadingWidget()
                sampleSize = min(self.width() / (batch_size + 2), self.height() / (num_batches + 2))
                sample.setGeometry(0, 0, sampleSize, sampleSize)
                self.samples.append(sample)
                self.gridLayout.addWidget(sample, row, column, 1, 1)
        self.setLayout(self.layout)
