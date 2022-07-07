from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QRect, QBuffer


class SampleWidget(QPushButton):
    """A button used to display and select an inpainting sample image."""
    def __init__(self):
        super().__init__()
        self._pixmap = None

    def loadImage(self, imageSample):
        self._imageSample = imageSample
        self.qim = QtGui.QImage(imageSample.tobytes("raw","RGB"),
                imageSample.width,
                imageSample.height,
                QtGui.QImage.Format_RGB888)
        self._pixmap = QtGui.QPixmap.fromImage(self.qim)
        minDim = min(self.width(), self.height())
        self._pixmap = self._pixmap.scaled(minDim, minDim)
        self.repaint()

    def resizeEvent(self, event):
        minDim = min(self.width(), self.height())
        if self._pixmap is not None:
            self._pixmap = self._pixmap.scaled(minDim, minDim)

    def paintEvent(self, event):
        painter = QPainter(self)
        minDim = min(self.width(), self.height())
        left = (self.width() - minDim) / 2
        top = (self.height() - minDim) / 2
        if self._pixmap is not None:
            painter.drawPixmap(QRect(left, top, minDim, minDim), self._pixmap)
        else: #Draw loading placeholder
            painter.setPen(QPen(Qt.black, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.fillRect(left, top, minDim, minDim, Qt.black)
            painter.setPen(QPen(Qt.white, 4, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawText(left + (minDim / 10), self.height() / 2, "Loading...")

class SampleSelector(QWidget):
    """Shows all inpainting samples as they load, allows the user to select one or discard all of them."""

    def __init__(self, batch_size, num_batches, applySample, closeSelector):
        """
        batch_size : int
            Number of image samples that will be generated per batch.
        num_batches : int
            Number of image sample batches that will be generated.
        applySample : function(Image)
            Function that will apply a selected sample image to the edited image, then close the SampleSelector.
        closeSelector : function()
            Function that will close the SampleSelector without selecting an image.
        """
        super().__init__()
        self._applySample = applySample
        self.selected = None
        self._nRows = num_batches
        self._nColumns = batch_size

        instructions = QLabel(self)
        instructions.setText("Click a sample to apply it to the source image, or click 'cancel' to discard all samples.")

        self._cancelButton = QPushButton(self)
        self._cancelButton.setText("cancel")
        self._cancelButton.clicked.connect(closeSelector)

        self._layout = QVBoxLayout()
        self._topBarLayout = QHBoxLayout()
        self._gridLayout = QGridLayout()
        self._layout.addLayout(self._topBarLayout, 1)
        self._layout.addLayout(self._gridLayout, 255)

        self._topBarLayout.addWidget(instructions, 10)
        self._topBarLayout.addWidget(self._cancelButton, 1)
        self._topBarLayout.setSpacing(max(2, self.height() // 30))
        for row in range(num_batches):
            self._gridLayout.setRowMinimumHeight(row, (self.height() * 0.95) // num_batches)
        for column in range(batch_size):
            self._gridLayout.setColumnMinimumWidth(column, (self.width() * 0.95) // batch_size)

        for row in range(num_batches):
            for column in range(batch_size):
                sampleWidget = SampleWidget()
                sampleSize = min(self.width() / batch_size, self.height() / num_batches)
                sampleWidget.setMinimumSize(sampleSize, sampleSize)
                self._gridLayout.addWidget(sampleWidget, row, column, 1, 1)
        self.setLayout(self._layout)

    def loadSample(self, imageSample, idx, batch):
        """
        Loads an inpainting sample image into the appropriate SampleWidget.
        Parameters:
        -----------
        imageSample : Image
            Newly generated inpainting image sample.
        idx : int
            Index of the image sample within its batch.
        batch : int
            Batch index of the image sample.
        """
        sampleIdx = idx + (batch * self._nRows)
        sampleWidget = self._gridLayout.itemAtPosition(batch, idx)
        if sampleWidget is not None:
            sampleWidget = sampleWidget.widget()
            sampleWidget.loadImage(imageSample)
            def selectOnClick():
                if imageSample == sampleWidget._imageSample:
                    self._applySample(imageSample)
            sampleWidget.clicked.connect(selectOnClick)

    def resizeEvent(self, event):
        sampleSize = min(self.width() / (self._nColumns + 2),
                self.height() / (self._nRows + 2))
        for row in range(self._nRows):
            for col in range(self._nColumns):
                sampleWidget = self._gridLayout.itemAtPosition(row, col)
                if sampleWidget is not None:
                    sampleWidget.widget().setMinimumSize(sampleSize, sampleSize)
