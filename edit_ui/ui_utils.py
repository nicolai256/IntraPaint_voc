from PIL import Image
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QBuffer, QPoint
import io

"""Adds general-purpose utility functions to reuse in UI code"""

def imageToQImage(pilImage):
    """Convert a PIL Image to a RGB888 formatted PyQt5 QImage."""
    if isinstance(pilImage, Image.Image):
        return QImage(pilImage.tobytes("raw","RGB"),pilImage.width,
                pilImage.height, QImage.Format_RGB888)

def qImageToImage(qImage):
    """Convert a PyQt5 QImage to a PIL image, in PNG format."""
    if isinstance(qImage, QImage):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        qImage.save(buffer, "PNG")
        pil_im = Image.open(io.BytesIO(buffer.data()))
        return pil_im

def getScaledPlacement(containerSize, innerSize, marginWidth=0):
    """
    Calculate the most appropriate placement of a scaled rectangle within a container, without changing aspect ratio.
    Parameters:
    -----------
    containerSize : list
        (width, height) of the container where the scaled rectangle will be placed.        
    innerSize : list
        (width, height) of the rectangle to be scaled and placed within the container.
    marginWidth : list
        Width in pixels of the area around the container edges that should remain empty.
    Returns:
    --------
    position : QPoint
        (x,y) coordinate where the scaled area should be placed
    scale : number
        Amount that the rectangle's width and height should be scaled.
    """
    for i in [0, 1]:
        containerSize[i] -= (marginWidth * 2)
    scale = min(containerSize[0]/innerSize[0], containerSize[1]/innerSize[1])
    coords = [marginWidth, marginWidth]
    for i in [0, 1]:
        if (innerSize[i] * scale) < containerSize[i]:
            coords[i] = marginWidth + (containerSize[i] - (innerSize[i] * scale)) / 2
    return QPoint(int(coords[0]), int(coords[1])), scale
