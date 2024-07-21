"""Tests for PDF module."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import modules.pdf_module as pdf
from modules.pdf_module import PdfImage, ImagePart


def test_combine_images():
    image_list = [PdfImage(image_bbox=[0,0,5,5], image_page=1, caption=None, image_parts=[ImagePart(xref=1, bbox=[0,0,5,5])])]
    result = pdf.combine_images(image_list)
    assert len(result) == 1
