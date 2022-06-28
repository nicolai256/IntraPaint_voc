from PyQt5.QtWidgets import *
from edit_ui.mask_creator import MaskCreator
from edit_ui.image_viewer import ImageViewer
import PyQt5.QtGui as QtGui

class MainWindow(QMainWindow):

    def __init__(self, width, height, im):
        super().__init__()
        # Main image view controls
        self.imageViewer = ImageViewer(im)
        self.fileSelectButton = QPushButton(self)
        self.fileSelectButton.setText("Select Image")
        self.fileTextBox = QLineEdit("Image Path goes here", self)
        self.imgReloadButton = QPushButton(self)
        self.imgReloadButton.setText("Reload image")
        self.xCoordBox = QSpinBox(self)
        self.yCoordBox = QSpinBox(self)
        imageViewLayout = QGridLayout()
        imageViewLayout.addWidget(self.imageViewer, 0, 0, 1, 14)
        imageViewLayout.addWidget(self.fileSelectButton, 1, 0, 1, 2)
        imageViewLayout.addWidget(self.fileTextBox, 1, 2, 1, 8)
        imageViewLayout.addWidget(self.imgReloadButton, 1, 10, 1, 2)
        imageViewLayout.addWidget(self.xCoordBox, 1, 12, 1, 1)
        imageViewLayout.addWidget(self.yCoordBox, 1, 13, 1, 1)

        #Image mask controls
        self.maskCreator = MaskCreator(im)
        self.selectMaskAreaButton = QPushButton(self)
        self.clearMaskButton = QPushButton(self)
        self.maskBrushSizeBox = QSpinBox(self)

        #Inpainting controls
        self.textPromptBox = QLineEdit("Image generation prompt here", self)
        self.batchSizeBox = QSpinBox(self)
        self.batchCountBox = QSpinBox(self)
        self.inpaintButton = QPushButton();
        self.saveButton = QPushButton(self)

        self.centralWidget = QWidget(self);
        self.setCentralWidget(self.centralWidget)
        self.layout = QGridLayout()
        #self.layout.addWidget(self.maskCreator, 0, 1, 1, 1)
        self.layout.addLayout(imageViewLayout, 0, 0, 2, 1)
        
        def selectArea():
            selection = self.imageViewer.getSelection()
            if selection is not None:
                self.maskCreator.loadImage(selection)

        self.button = QPushButton(self)
        self.button.clicked.connect(selectArea)

        
        
        self.centralWidget.setLayout(self.layout)

        self.setGeometry(0, 0, im.width, im.height)
        self.resize(self.maskCreator.image.width() * 4, self.maskCreator.image.height() * 4)
        self.show()

    def getCanvas(self):
        return self.maskCreator.getCanvas()
