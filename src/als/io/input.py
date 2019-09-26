"""
Provides everything need to handle ALS main inputs : images.

We need to read file and in the future, get images from INDI
"""
import logging
from abc import abstractmethod
from pathlib import Path

import numpy as np
import rawpy
from PyQt5.QtCore import QObject
from astropy.io import fits

from als.model import Image

_LOGGER = logging.getLogger(__name__)


class InputListener(QObject):
    """
    In charge of input management, **abstract class**
    """

    @staticmethod
    def create_listener(listener_type: str):
        """
        Creates specialized input listeners.

        :param listener_type: what type of listener to create
        :type listener_type: str : allowed values :

          - 'FS' to create a filesystem listener

        :return: an input listener
        :rtype: FileSystemListener
        """
        pass

    @abstractmethod
    def start(self):
        """
        Start listening for new images.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop listening for new images.
        """
        pass


class FileSystemListener(InputListener):
    """
    Watches file changes (creation, move) in a specific filesystem folder
    """
    pass


def read_image(path: Path):
    """
    Reads an image from disk

    :param path: path to the file to load image from
    :type path:  pathlib.Path

    :return: the image read from disk
    :rtype: Image
    """
    if path.suffix.lower() in ['.fit', '.fits']:
        return _read_fit_image(path)

    return _read_raw_image(path)


def _read_fit_image(path: Path):
    """
    read FIT image from filesystem

    :param path: path to image file to load from
    :type path: pathlib.Path

    :return: the loaded image, with data and headers parsed
    :rtype: Image
    """
    with fits.open(str(path.resolve())) as fit:
        data = fit[0].data
        header = fit[0].header

    image = Image(data)

    if 'BAYERPAT' in header:
        image.bayer_pattern = header['BAYERPAT']

    return image


def _read_raw_image(path: Path):
    """
    Reads a RAW DLSR image from file

    :param path: path to the file to read from
    :type path: pathlib.Path

    :return: the image
    :rtype: Image
    """
    raw_image = rawpy.imread(str(path.resolve())).postprocess(gamma=(1, 1),
                                                              no_auto_bright=True,
                                                              output_bps=16,
                                                              user_flip=0)
    return Image(np.rollaxis(raw_image, 2, 0))
