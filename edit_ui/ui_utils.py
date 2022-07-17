from PIL import Image
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QBuffer, QPoint, QRect, QSize, QMargins
import io

"""Adds general-purpose utility functions to reuse in UI code"""

def imageToQImage(pilImage):
    """Convert a PIL Image to a RGB888 formatted PyQt5 QImage."""
    if isinstance(pilImage, Image.Image):
        return QImage(pilImage.tobytes("raw","RGB"),
                pilImage.width,
                pilImage.height,
                pilImage.width * 3,
                QImage.Format_RGB888)

def qImageToImage(qImage):
    """Convert a PyQt5 QImage to a PIL image, in PNG format."""
    if isinstance(qImage, QImage):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        qImage.save(buffer, "PNG")
        pil_im = Image.open(io.BytesIO(buffer.data()))
        return pil_im

def getScaledPlacement(containerRect, innerSize, marginWidth=0):
    """
    Calculate the most appropriate placement of a scaled rectangle within a container, without changing aspect ratio.
    Parameters:
    -----------
    containerRect : QRect
        Bounds of the container where the scaled rectangle will be placed.        
    innerSize : QSize
        S of the rectangle to be scaled and placed within the container.
    marginWidth : int
        Distance in pixels of the area around the container edges that should remain empty.
    Returns:
    --------
    placement : QRect
        Size and position of the scaled rectangle within containerRect.
    scale : number
        Amount that the inner rectangle's width and height should be scaled.
    """
    containerSize = containerRect.size() - QSize(marginWidth * 2, marginWidth * 2)
    scale = min(containerSize.width()/innerSize.width(), containerSize.height()/innerSize.height())
    x = containerRect.x() + marginWidth
    y = containerRect.y() + marginWidth
    if (innerSize.width() * scale) < containerSize.width():
        x += (containerSize.width() - innerSize.width() * scale) / 2
    if (innerSize.height() * scale) < containerSize.height():
        y += (containerSize.height() - innerSize.height() * scale) / 2
    return QRect(int(x), int(y), int(innerSize.width() * scale), int(innerSize.height() * scale))

def QEqualMargins(size):
    """Returns a QMargins object that is equally spaced on all sides."""
    return QMargins(size, size, size, size)

def showErrorDialog(parent, title, text):
    """Opens a message box to show some text to the user."""
    messageBox = QMessageBox(parent)
    messageBox.setWindowTitle(title)
    messageBox.setText(text)
    messageBox.setStandardButtons(QMessageBox.Ok)
    messageBox.exec()
