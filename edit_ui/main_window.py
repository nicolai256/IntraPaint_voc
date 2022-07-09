from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QObject, QThread, QRect, QPoint, pyqtSignal
from edit_ui.mask_panel import MaskPanel
from edit_ui.image_panel import ImagePanel
from edit_ui.inpainting_panel import InpaintingPanel
from edit_ui.sample_selector import SampleSelector
import PyQt5.QtGui as QtGui
from PIL import Image, ImageFilter

class MainWindow(QMainWindow):
    """Creates a user interface to simplify repeated inpainting operations on image sections."""

    def __init__(self, width, height, im, doInpaint):
        """
        Parameters:
        -----------
        width : int
            Initial window width in pixels.
        height : int
            Initial window height in pixels
        im : Image (optional)
            Optional initial image to edit.
        doInpaint : function(Image selection, Image mask, string prompt, int batchSize int, batchCount)
            Function used to trigger inpainting on a selected area of the edited image.
        """
        super().__init__()

        self.imagePanel = ImagePanel(im)
        self.maskPanel = MaskPanel(im,
                lambda: self.imagePanel.imageViewer.getSelectedSection(),
                self.imagePanel.imageViewer.onSelection)
        self._draggingDivider = False

        def inpaintAndShowSamples(selection, mask, prompt, batchSize, batchCount):
            self.thread = QThread()
            class InpaintThreadWorker(QObject):
                finished = pyqtSignal()
                shouldRedraw = pyqtSignal()
                def run(self):
                    doInpaint(selection, mask, prompt, batchSize, batchCount,
                            loadSamplePreview)
                    self.finished.emit()
            self.worker = InpaintThreadWorker()

            def closeSampleSelector():
                selector = self.centralWidget.currentWidget()
                if selector is not self.mainWidget:
                    self.centralWidget.setCurrentWidget(self.mainWidget)
                    self.centralWidget.removeWidget(selector)
                    self.update()
            def selectSample(pilImage):
                self.imagePanel.imageViewer.insertIntoSelection(pilImage)
                closeSampleSelector()
            def loadSamplePreview(img, y, x):
                # Inpainting can create subtle changes outside the mask area, which can gradually impact image quality
                # and create annoying lines in larger images. To fix this, apply the mask to the resulting sample, and
                # re-combine it with the original image. In addition, blur the mask slightly to improve image composite
                # quality.
                maskAlpha = mask.convert('L').point( lambda p: 255 if p < 1 else 0 ).filter(ImageFilter.GaussianBlur())
                cleanImage = Image.composite(selection, img, maskAlpha)
                sampleSelector.loadSample(cleanImage, y, x)
                self.worker.shouldRedraw.emit()
                self.thread.usleep(10) # Briefly pausing the inpainting thread gives the UI thread a chance to redraw.

            sampleSelector = SampleSelector(batchSize,
                    batchCount,
                    selectSample,
                    closeSampleSelector)
            self.centralWidget.addWidget(sampleSelector)
            self.centralWidget.setCurrentWidget(sampleSelector)
            sampleSelector.setIsLoading(True)
            self.update()

            self.worker.shouldRedraw.connect(lambda: sampleSelector.repaint())
            self.worker.finished.connect(lambda: sampleSelector.setIsLoading(False))
            self.thread.started.connect(self.worker.run)
            self.thread.finished.connect(self.thread.deleteLater)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.start()

        self.inpaintPanel = InpaintingPanel(
                inpaintAndShowSamples,
                lambda: self.imagePanel.imageViewer.getImage(),
                lambda: self.imagePanel.imageViewer.getSelectedSection(),
                lambda: self.maskPanel.getMask())

        self.setGeometry(0, 0, width, height)
        self.layout = QGridLayout()
        self.layout.addWidget(self.imagePanel, 0, 0, 1, 1)
        self.layout.addWidget(self.maskPanel, 0, 2, 1, 1)
        self.layout.addWidget(self.inpaintPanel, 2, 0, 1, 2)
        self.layout.setRowStretch(0, 100)
        self.layout.setColumnStretch(0, 250)
        self.layout.setColumnStretch(1, 5)
        self.layout.setColumnStretch(2, 50)
        self.layout.setColumnMinimumWidth(2, 300)
        self.mainWidget = QWidget(self);
        self.mainWidget.setLayout(self.layout)

        self.centralWidget = QStackedWidget(self);
        self.centralWidget.addWidget(self.mainWidget)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setCurrentWidget(self.mainWidget)

    def applyArgs(self, args):
        """Applies optional command line arguments to the UI."""
        if args.init_image:
            image = Image.open(open(args.init_image, 'rb')).convert('RGB')
            self.imagePanel.imageViewer.loadImage(image)
            self.imagePanel.fileTextBox.setText(args.init_image)
        if args.text:
            self.inpaintPanel.textPromptBox.setText(args.text)
        if args.num_batches:
            self.inpaintPanel.batchCountBox.setValue(args.num_batches)
        if args.batch_size:
            self.inpaintPanel.batchSizeBox.setValue(args.batch_size)

    def getMask(self):
        return self.maskPanel.getMask()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.centralWidget.currentWidget() is self.mainWidget:
            painter = QPainter(self)
            color = Qt.green if self._draggingDivider else Qt.black
            size = 4 if self._draggingDivider else 2
            painter.setPen(QPen(color, size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            dividerBox = self._dividerCoords()
            yMid = dividerBox.y() + (dividerBox.height() // 2)
            midLeft = QPoint(dividerBox.x(), yMid)
            midRight = QPoint(dividerBox.right(), yMid)
            arrowWidth = dividerBox.width() // 4
            # Draw arrows:
            painter.drawLine(midLeft, midRight)
            painter.drawLine(midLeft, dividerBox.topLeft() + QPoint(arrowWidth, 0))
            painter.drawLine(midLeft, dividerBox.bottomLeft() + QPoint(arrowWidth, 0))
            painter.drawLine(midRight, dividerBox.topRight() - QPoint(arrowWidth, 0))
            painter.drawLine(midRight, dividerBox.bottomRight() - QPoint(arrowWidth, 0))

    def _dividerCoords(self):
        imageRight = self.imagePanel.x() + self.imagePanel.width()
        maskLeft = self.maskPanel.x()
        width = (maskLeft - imageRight) // 2
        height = width // 2
        x = imageRight + (width // 2)
        y = self.imagePanel.y() + (self.imagePanel.height() // 2) - (height // 2)
        return QRect(x, y, width, height)

    def mousePressEvent(self, event):
        if self.centralWidget.currentWidget() is self.mainWidget and self._dividerCoords().contains(event.pos()):
            self._draggingDivider = True
            self.update()

    def mouseMoveEvent(self, event):
        if event.buttons() and self._draggingDivider:
            x = event.pos().x()
            imgWeight = int(x / self.width() * 300)
            maskWeight = 300 - imgWeight
            self.layout.setColumnStretch(0, imgWeight)
            self.layout.setColumnStretch(2, maskWeight)
            self.update()

    def mouseReleaseEvent(self, event):
        if self._draggingDivider:
            self._draggingDivider = False
            self.update()
