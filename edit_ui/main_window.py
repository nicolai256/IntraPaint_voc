from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from edit_ui.mask_panel import MaskPanel
from edit_ui.image_panel import ImagePanel
from edit_ui.inpainting_panel import InpaintingPanel
from edit_ui.sample_selector import SampleSelector
import PyQt5.QtGui as QtGui
from PIL import Image

class MainWindow(QMainWindow):

    def __init__(self, width, height, im, doInpaint):
        super().__init__()

        self.imagePanel = ImagePanel(im)
        self.maskPanel = MaskPanel(im,
                lambda: self.imagePanel.imageViewer.getSelectedSection(),
                self.imagePanel.imageViewer.onSelection)

        def inpaintAndShowSamples(selection, mask, prompt, batchSize, batchCount):
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
                self.update()
            sampleSelector = SampleSelector(self.width(),
                    self.height(),
                    batchSize,
                    batchCount,
                    selectSample,
                    closeSampleSelector)
            self.centralWidget.addWidget(sampleSelector)
            self.centralWidget.setCurrentWidget(sampleSelector)
            self.update()
            class InpaintThread(QObject):
                finished = pyqtSignal()
                def run(self):
                    doInpaint(selection, mask, prompt, batchSize, batchCount,
                            loadSamplePreview)
                    self.finished.emit()
            self.worker = InpaintThread()
            self.thread = QThread()
            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
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
