from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from edit_ui.mask_panel import MaskPanel
from edit_ui.image_panel import ImagePanel
from edit_ui.inpainting_panel import InpaintingPanel
from edit_ui.sample_selector import SampleSelector
import PyQt5.QtGui as QtGui
from PIL import Image

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
                sampleSelector.loadSample(img, y, x)
                self.worker.shouldRedraw.emit()
                self.thread.usleep(10) # Briefly pausing the inpainting thread gives the UI thread a chance to redraw.

            sampleSelector = SampleSelector(batchSize,
                    batchCount,
                    selectSample,
                    closeSampleSelector)
            self.centralWidget.addWidget(sampleSelector)
            self.centralWidget.setCurrentWidget(sampleSelector)
            self.update()

            self.worker.shouldRedraw.connect(lambda: sampleSelector.repaint())
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
        self.layout.addWidget(self.maskPanel, 0, 1, 1, 1)
        self.layout.addWidget(self.inpaintPanel, 2, 0, 1, 2)
        self.layout.setRowStretch(0, 100)
        self.layout.setColumnStretch(0, 255)
        self.layout.setColumnStretch(1, 55)
        self.layout.setColumnMinimumWidth(1, 300)
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
