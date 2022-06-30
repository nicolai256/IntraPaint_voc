from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from edit_ui.mask_panel import MaskPanel
from edit_ui.image_panel import ImagePanel
from edit_ui.inpainting_panel import InpaintingPanel
import PyQt5.QtGui as QtGui
from PIL import Image

class MainWindow(QMainWindow):

    def __init__(self, width, height, im, doInpaint):
        super().__init__()

        self.imagePanel = ImagePanel(im)
        self.maskPanel = MaskPanel(im, lambda: self.imagePanel.getSelection())
        self.inpaintPanel = InpaintingPanel(
                lambda sel, mask, txt, sz, ct: doInpaint(self, sel, mask, txt, sz, ct),\
                lambda: self.imagePanel.getImage(), \
                lambda: self.imagePanel.getSelection(), \
                lambda: self.maskPanel.getMask())
        def writeMaskIntoImage():
            mask = self.maskPanel.getMask()
            if mask is not None:
                self.imagePanel.imageViewer.insertIntoSelection(mask)
        self.inpaintPanel.saveButton.clicked.connect(writeMaskIntoImage)


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
