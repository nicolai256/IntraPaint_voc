from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QObject, QThread, QRect, QPoint, QSize, pyqtSignal
from edit_ui.mask_panel import MaskPanel
from edit_ui.image_panel import ImagePanel
from edit_ui.inpainting_panel import InpaintingPanel
from edit_ui.sample_selector import SampleSelector
from edit_ui.ui_utils import showErrorDialog
import PyQt5.QtGui as QtGui
from PIL import Image, ImageFilter
import sys

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
        self.thread = None

        def inpaintAndShowSamples(selection, mask, prompt, batchSize, batchCount, negative, guidanceScale, skipSteps):
            if selection is None:
                showErrorDialog(self, "Failed", "Load an image for editing before trying to start inpainting.")
                return
            if self.thread is not None:
                showErrorDialog(self, "Failed", "Existing inpainting operation not yet finished, wait a little longer.")
                return
            self.thread = QThread()


            # If sketch mode was used, write the sketch onto the image selection:
            inpaintImage = selection
            inpaintMask = mask
            sketchImage = self.maskPanel.maskCreator.getSketch()
            if sketchImage is not None:
                if sketchImage.width != inpaintImage.width or sketchImage.height != inpaintImage.height:
                    sketchImage = sketchImage.resize(inpaintImage.width, inpaintImage.height).convert('RGBA')
                inpaintImage = inpaintImage.convert('RGBA')
                inpaintImage = Image.alpha_composite(inpaintImage, sketchImage).convert('RGB')
            keepSketch = (sketchImage is not None) and self.maskPanel.keepSketchCheckbox.isChecked()

            # If scaling is enabled, scale selection as close to 256x256 as possible while attempting to minimize
            # aspect ratio changes. Keep the unscaled version so it can be used for compositing if "keep sketch"
            # is checked.
            unscaledInpaintImage = inpaintImage

            if self.inpaintPanel.scalingEnabled():
                largestDim = max(selection.width, selection.height)
                scale = 256 / largestDim
                width = int(selection.width * scale + 1)
                width = max(64, width - (width % 64))
                height = int(selection.height * scale + 1)
                height = max(64, height - (height % 64))
                inpaintImage = inpaintImage.resize((width, height))
                inpaintMask = mask.resize((width, height))
            elif inpaintMask.width != inpaintImage.width or inpaintMask.height != inpaintImage.height:
                inpaintMask = mask.resize((inpaintImage.width, inpaintImage.height))



            class InpaintThreadWorker(QObject):
                finished = pyqtSignal()
                imageReady = pyqtSignal(Image.Image, int, int)
                errorSignal = pyqtSignal(str)
                def run(self):
                    def sendImage(img, y, x):
                        if img.width != selection.width or img.height != selection.height:
                            img = img.resize((selection.width, selection.height))
                        self.imageReady.emit(img, y, x)
                    try:
                        doInpaint(inpaintImage,
                                    inpaintMask,
                                    prompt,
                                    batchSize,
                                    batchCount,
                                    sendImage,
                                    negative,
                                    guidanceScale,
                                    skipSteps)
                    except Exception as err:
                        print(f'Inpainting failure: {err}')
                        self.errorSignal.emit(str(err))
                    self.finished.emit()
            self.worker = InpaintThreadWorker()
            self.worker.moveToThread(self.thread)

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
                cleanImage = Image.composite(unscaledInpaintImage if keepSketch else selection,
                        img,
                        maskAlpha)
                sampleSelector.loadSampleImage(cleanImage, y, x)
                sampleSelector.repaint()

            sampleSelector = SampleSelector(batchSize,
                    batchCount,
                    (unscaledInpaintImage if keepSketch else selection).convert('RGB'),
                    mask,
                    selectSample,
                    closeSampleSelector)
            self.centralWidget.addWidget(sampleSelector)
            self.centralWidget.setCurrentWidget(sampleSelector)
            sampleSelector.setIsLoading(True)
            self.update()

            def handleError(err):
                closeSampleSelector()
                showErrorDialog(self, "Inpainting failure", err)
            self.worker.errorSignal.connect(handleError)
            self.worker.imageReady.connect(loadSamplePreview)
            self.worker.finished.connect(lambda: sampleSelector.setIsLoading(False))
            self.thread.started.connect(self.worker.run)
            self.thread.finished.connect(self.thread.deleteLater)
            def clearOldThread():
                self.thread = None
            self.thread.finished.connect(clearOldThread)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.start()

        self.inpaintPanel = InpaintingPanel(
                inpaintAndShowSamples,
                lambda: self.imagePanel.imageViewer.getImage(),
                lambda: self.imagePanel.imageViewer.getSelectedSection(),
                lambda: self.maskPanel.getMask())
        self.inpaintPanel.enableScaleToggled.connect(lambda v: self.imagePanel.setScaleEnabled(v))

        self.layout = QVBoxLayout()

        self.imageLayout = QHBoxLayout()
        self.imageLayout.addWidget(self.imagePanel, stretch=255)
        self.imageLayout.addSpacing(30)
        self.imageLayout.addWidget(self.maskPanel, stretch=100)
        self.layout.addLayout(self.imageLayout, stretch=255)

        self.layout.addWidget(self.inpaintPanel, stretch=20)
        self.mainWidget = QWidget(self);
        self.mainWidget.setLayout(self.layout)

        self.centralWidget = QStackedWidget(self);
        self.centralWidget.addWidget(self.mainWidget)
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setCurrentWidget(self.mainWidget)

    def applyArgs(self, args):
        """Applies optional command line arguments to the UI."""
        if args.text:
            self.inpaintPanel.textPromptBox.setText(args.text)
        if ('init_edit_image' in args) and args.init_edit_image:
            self.imagePanel.loadImage(args.init_edit_image)
            self.imagePanel.fileTextBox.setText(args.init_edit_image)
        if ('num_batches' in args) and args.num_batches:
            self.inpaintPanel.batchCountBox.setValue(args.num_batches)
        if ('batch_size' in args) and args.batch_size:
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
            self.imageLayout.setStretch(0, imgWeight)
            self.imageLayout.setStretch(2, maskWeight)
            self.update()

    def mouseReleaseEvent(self, event):
        if self._draggingDivider:
            self._draggingDivider = False
            self.update()
