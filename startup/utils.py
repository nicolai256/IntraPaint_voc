# Define miscellaneous utility functions
from PIL import Image
import base64
import requests
import io

def fetch(url_or_path):
    """Open a file from either a path or a URL."""
    if str(url_or_path).startswith('http://') or str(url_or_path).startswith('https://'):
        r = requests.get(url_or_path)
        r.raise_for_status()
        fd = io.BytesIO()
        fd.write(r.content)
        fd.seek(0)
        return fd
    return open(url_or_path, 'rb')

def imageToBase64(pilImage):
    buffer = io.BytesIO()
    pilImage.save(buffer, format='PNG')
    return str(base64.b64encode(buffer.getvalue()), 'utf-8')

def loadImageFromBase64(imageStr):
    return Image.open(io.BytesIO(base64.b64decode(imageStr)))
