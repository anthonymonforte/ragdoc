"""Tests for PDF module."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511

import sys
import os
from typing import List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import modules.pdf_module as pdf
from modules.pdf_module import PdfImage, ImagePart

def create_pdf_image_obj(image_bbox: List[float], page: int, xref: int):    
    return PdfImage(image_bbox=image_bbox, image_page=page, caption=None, image_parts=[ImagePart(xref=xref, bbox=image_bbox)])

def test_combine_images_should_not_combine_separate_images():
    image_list = [create_pdf_image_obj([0,0,0,5], 1, 1),
                  create_pdf_image_obj([0,10,0,15], 1, 2)]
    result = pdf.combine_images(image_list)
    assert len(result) == 2
    assert len(result[0].image_parts) == 1
    assert len(result[1].image_parts) == 1


def test_combine_images_should_combine_image_parts():
    image_list = [create_pdf_image_obj([0,0,0,5], 1, 1),
                  create_pdf_image_obj([0,5,0,15], 1, 2)]
    result = pdf.combine_images(image_list)
    assert len(result) == 1
    assert len(result[0].image_parts) == 2

def test_combine_images_should_combine_image_parts_within_threshold():
    image_list = [create_pdf_image_obj([0,0,0,5], 1, 1),
                  create_pdf_image_obj([0,5 + pdf.IMAGE_OFFSET_THRESHOLD,0,15], 1, 2)]
    result = pdf.combine_images(image_list)
    assert len(result) == 1
    assert len(result[0].image_parts) == 2

def test_combine_images_should_not_combine_image_parts_outside_threshold():
    image_list = [create_pdf_image_obj([0,0,0,5], 1, 1),
                  create_pdf_image_obj([0,5 + pdf.IMAGE_OFFSET_THRESHOLD + .01,0,15], 1, 2)]
    result = pdf.combine_images(image_list)
    assert len(result) == 2
    assert len(result[0].image_parts) == 1
    assert len(result[1].image_parts) == 1
